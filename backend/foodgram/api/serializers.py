from django.conf import settings
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework.exceptions import ValidationError
from rest_framework.fields import (
    CharField, IntegerField, SerializerMethodField)
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import BooleanField, ModelSerializer

from recipes.constants import MAX_LENGTH_NAME_RECIPE
from recipes.models import Ingredient, Recipe, RecipeIngredient, ShortLink, Tag
from users.models import Subscribe, User


class TagSerializer(ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class AvatarSerializer(UserSerializer):
    avatar = Base64ImageField()

    class Meta:
        model = User
        fields = ('avatar',)


class UserSignUpSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')


class CustomUserSerializer(UserSerializer):
    is_subscribed = SerializerMethodField(read_only=True)
    avatar = Base64ImageField(required=False)

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Subscribe.objects.filter(user=user, author=author).exists()


class SubscribeSerializer(CustomUserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes_count',
                                                     'recipes')
        read_only_fields = ('email', 'username')

    def validate(self, data):
        author = self.instance
        user = self.context.get('request').user
        if Subscribe.objects.filter(author=author, user=user).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя!')
        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя!')
        return data

    def get_recipes_count(self, author):
        return author.recipes.count()

    def get_recipes(self, author):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes = author.recipes.all()
        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeShortSerializer(recipes, many=True, read_only=True)
        return serializer.data


class RecipeIngredientsSerializer(ModelSerializer):
    name = SerializerMethodField()
    measurement_unit = SerializerMethodField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')

    def get_name(self, obj):
        return obj.ingredient.name

    def get_measurement_unit(self, obj):
        return obj.ingredient.measurement_unit


class RecipeIngredientCreateSerializer(ModelSerializer):
    """Сериализатор для создания ингредиентов рецепта."""
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(ModelSerializer):
    """Сериализатор для получения рецепта."""

    author = CustomUserSerializer(read_only=True)
    tags = TagSerializer(many=True, required=True)
    ingredients = RecipeIngredientsSerializer(
        many=True,
        source='recipeingredients',
        required=True
    )
    is_favorited = BooleanField(default=False)
    is_in_shopping_cart = BooleanField(default=False)
    image = Base64ImageField(required=True)

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time'
        )
        read_only_fields = ('author', 'tags', 'ingredients')


class IngredientCreateSerializer(ModelSerializer):
    """Серилизатор для Проверки ингредиента при создании рецепта."""

    id = IntegerField()
    amount = IntegerField(write_only=True)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')

    def validate_amount(self, value):
        if value < 1:
            raise ValidationError(
                'Количество должно быть больше или равно 1'
            )
        return value


class RecipeCreateSerializer(ModelSerializer):
    """Серилизатор для Создания и обновления рецептов."""

    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
        required=True
    )
    ingredients = IngredientCreateSerializer(
        write_only=True,
        many=True,
        required=True
    )
    image = Base64ImageField(required=True)
    name = CharField(max_length=MAX_LENGTH_NAME_RECIPE)
    text = CharField()
    cooking_time = IntegerField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'ingredients', 'image',
                  'name', 'text', 'cooking_time')

    def validate_cooking_time(self, value):

        if value <= 0:
            raise ValidationError(
                'Время приготовления должно быть больше 0'
            )
        return value

    def validate_image(self, value):
        """Проверяет, что изображение предоставлено."""
        if value is None:
            raise ValidationError('Поле image обязательно.')
        return value

    def validate(self, data):
        """Проверяет, что ингредиенты и теги уникальны и существуют."""

        ingredients = data.get('ingredients', [])

        if not ingredients:
            raise ValidationError('Поле ingredients обязательно.')

        ingredienеts_list = [ingredient['id'] for ingredient in ingredients]
        if len(ingredienеts_list) != len(set(ingredienеts_list)):
            raise ValidationError(
                'Ингредиенты должны быть уникальными.')

        non_existing_ingredients = [
            ingredient_id for ingredient_id in ingredienеts_list
            if not Ingredient.objects.filter(id=ingredient_id).exists()
        ]
        if non_existing_ingredients:
            raise ValidationError(
                f'Ингредиент с id {non_existing_ingredients} не существует.'
            )

        tags = data.get('tags', [])
        if not tags:
            raise ValidationError('Поле tags обязательно.')
        if len(tags) != len(set(tags)):
            raise ValidationError('Теги должны быть уникальными.')

        return data

    @transaction.atomic
    def create(self, validated_data):
        """Создает новый рецепт."""
        author = self.context.get('request').user
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        validated_data.pop('author', None)
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)

        ingredient_ids = [ingredient_data.get('id')
                          for ingredient_data in ingredients_data]
        ingredients = Ingredient.objects.filter(id__in=ingredient_ids)
        ingredient_dict = {
            ingredient.id: ingredient for ingredient in ingredients}

        recipe_ingredients = []
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data.get('id')
            amount = ingredient_data.get('amount')
            ingredient = ingredient_dict.get(ingredient_id)
            if ingredient:
                recipe_ingredients.append(
                    RecipeIngredient(
                        recipe=recipe,
                        ingredient=ingredient,
                        amount=amount
                    )
                )
        RecipeIngredient.objects.bulk_create(recipe_ingredients)
        return recipe

    def create_ingredients(self, ingredients, recipe):
        """Создает и связывает ингредиенты с рецептом."""

        ingredient_ids = [ingredient['id'] for ingredient in ingredients]
        ingredient_instances = Ingredient.objects.filter(id__in=ingredient_ids)
        ingredient_dict = {
            ingredient.id: ingredient for ingredient in ingredient_instances}
        ingredients_list = [
            RecipeIngredient(
                recipe=recipe,
                amount=ingredient['amount'],
                ingredient=ingredient_dict[ingredient['id']]
            )
            for ingredient in ingredients
        ]
        RecipeIngredient.objects.bulk_create(ingredients_list)

    @transaction.atomic
    def update(self, instance, validated_data):
        """Обновляет существующий рецепт."""
        tags = validated_data.pop('tags', None)
        ingredients = validated_data.pop('ingredients', None)

        if ingredients is None:
            raise ValidationError(
                'Поле "ingredients" обязательно для обновления рецепта.')
        instance = super().update(instance, validated_data)

        if tags is not None:
            instance.tags.set(tags)
        if ingredients is not None:
            instance.ingredients.clear()
            self.create_ingredients(ingredients, instance)
        instance.save()

        return instance

    def to_representation(self, instance):
        """Используем RecipeGetSerializer для формирования ответа."""
        return RecipeGetSerializer(instance, context=self.context).data


class RecipeShortSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShortLinkSerializer(ModelSerializer):
    """Сериализатор для короткой ссылки."""
    short_link = SerializerMethodField()

    class Meta:
        model = ShortLink
        fields = ('short_link',)

    def get_short_link(self, obj):
        """Создает полный URL для короткой ссылки."""
        base_url = f'{settings.SITE_HOSTNAME}/s/'
        return f'{base_url}{obj.short_link}'

    def to_representation(self, instance):
        """Преобразует ключи в формат с дефисом."""
        representation = super().to_representation(instance)
        return {
            'short-link': representation['short_link']
        }
