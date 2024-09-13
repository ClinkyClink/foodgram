from django.db import transaction
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.fields import IntegerField, SerializerMethodField
from rest_framework.relations import PrimaryKeyRelatedField
from rest_framework.serializers import ModelSerializer, ReadOnlyField

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField

from recipes.models import Ingredient, RecipeIngredient, Recipe, Tag, ShoppingList, Favorite
from users.models import Subscribe, User
from .utils import create_ingredients


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

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, author):
        user = self.context.get('request').user
        if not user.is_authenticated:
            return False
        return Subscribe.objects.filter(user=user, author=author).exists()


class SubscribeSerializer(CustomUserSerializer):
    recipes_count = SerializerMethodField()
    recipes = SerializerMethodField()

    class Meta(CustomUserSerializer.Meta):
        fields = CustomUserSerializer.Meta.fields + ('recipes_count', 'recipes')
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
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all(),
                                            source='name.id')
    name = ReadOnlyField(source='name.name')
    measurement_unit = ReadOnlyField(
        source='name.measurement_unit',)

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientCreateSerializer(ModelSerializer):
    """Сериализатор для создания ингредиентов рецепта."""
    id = PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class RecipeGetSerializer(ModelSerializer):
    ingredients = RecipeIngredientsSerializer(many=True, source='recipeingredients')
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    is_favorited = SerializerMethodField()
    is_in_shopping_cart = SerializerMethodField()
    image = Base64ImageField(required=False)

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time')

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and Favorite.objects.filter(user=request.user, recipe=obj).exists())

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return (request and request.user.is_authenticated
                and ShoppingList.objects.filter(user=request.user, recipe=obj).exists())


class RecipeCreateSerializer(ModelSerializer):
    ingredients = RecipeIngredientCreateSerializer(many=True)
    tags = PrimaryKeyRelatedField(queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'image', 'name', 'text', 'cooking_time')

    def validate(self, data):
        ingredients_list = []
        for ingredient_data in data.get('ingredients'):
            if ingredient_data.get('amount') <= 0:
                raise ValidationError('Количество ингредиента должно быть больше 0')
            ingredients_list.append(ingredient_data.get('id'))
        if len(set(ingredients_list)) != len(ingredients_list):
            raise ValidationError('Нельзя добавить один и тот же ингредиент дважды')
        return data

    @transaction.atomic
    def create(self, validated_data):
        validated_data.pop('author', None)
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=self.context['request'].user, **validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        instance.tags.set(tags)
        RecipeIngredient.objects.filter(recipe=instance).delete()
        for ingredient_data in ingredients_data:
            RecipeIngredient.objects.create(
                recipe=instance,
                ingredient=ingredient_data['id'],
                amount=ingredient_data['amount']
            )
        return super().update(instance, validated_data)


class RecipeShortSerializer(ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
