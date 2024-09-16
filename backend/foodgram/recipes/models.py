import random
from string import ascii_letters, digits

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models

from .constants import (
    MAX_LENGTH_NAME_INGREDIENT, MAX_LENGTH_NAME_RECIPE, MAX_LENGTH_SHORTLINK,
    MAX_LENGTH_SLUG, MAX_LENGTH_TAG, MAX_LENGTH_UNIT)

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField('Название',
                            max_length=MAX_LENGTH_NAME_INGREDIENT,
                            db_index=True)
    measurement_unit = models.CharField('Единица измерения',
                                        max_length=MAX_LENGTH_UNIT)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField('Название',
                            unique=True,
                            max_length=MAX_LENGTH_TAG)
    slug = models.SlugField('Слаг',
                            unique=True,
                            max_length=MAX_LENGTH_SLUG)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField('Название',
                            max_length=MAX_LENGTH_NAME_RECIPE,
                            db_index=True)
    author = models.ForeignKey(
        User,
        related_name='recipes',
        on_delete=models.CASCADE,
        verbose_name='Автор рецепта'
    )
    image = models.ImageField('Изображение', upload_to='recipes/images')
    text = models.TextField('Описание')
    cooking_time = models.PositiveIntegerField(
        'Время приготовления (мин)',
        validators=[MinValueValidator(1)]
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        verbose_name='Теги'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Ингредиенты'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель для связи рецептов и ингредиентов с количеством."""

    amount = models.PositiveIntegerField(
        'Количество',
        validators=[MinValueValidator(1)]
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='recipeingredients',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredientrecipes',
        verbose_name='Ингредиент'
    )

    class Meta:
        verbose_name = 'Ингредиент рецепта'
        verbose_name_plural = 'Ингредиенты рецепта'
        constraints = [
            models.UniqueConstraint(fields=['recipe', 'ingredient'],
                                    name='unique_recipe_ingredient'),
            models.CheckConstraint(
                check=models.Q(recipeingredients__isnull=False),
                name='recipe_must_have_ingredients'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} в {self.recipe.name}: '
            f'{self.amount} {self.ingredient.measurement_unit}'
        )

    def clean(self):
        super().clean()
        if not self.recipeingredients.exists():
            raise ValidationError('Нельзя сохранить рецепт без ингредиентов.')
        for recipe_ingredient in self.recipeingredients.all():
            if not recipe_ingredient.ingredient:
                raise ValidationError("Ингредиент должен быть выбран.")
            if recipe_ingredient.amount < 1:
                raise ValidationError("Количество должно быть больше 0.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Favorite(models.Model):
    """Модель избранных рецептов."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_favorite')
        ]
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в Избранное'


class ShoppingList(models.Model):
    """Модель списка покупок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'recipe'],
                                    name='unique_shopping_cart')
        ]
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в свою корзину'


class ShortLink(models.Model):
    """Модель для хранения коротких ссылок на рецепты."""

    recipe = models.OneToOneField(Recipe, on_delete=models.CASCADE,
                                  related_name='short_link')
    short_link = models.CharField(max_length=MAX_LENGTH_SHORTLINK, unique=True,
                                  blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.short_link:
            self.short_link = self.generate_short_link()
        super().save(*args, **kwargs)

    def generate_short_link(self):
        """Генерирует уникальную короткую ссылку."""
        length = MAX_LENGTH_SHORTLINK
        characters = ascii_letters + digits
        while True:
            short_link = ''.join(random.choices(characters, k=length))
            if not ShortLink.objects.filter(short_link=short_link).exists():
                break
        return short_link
