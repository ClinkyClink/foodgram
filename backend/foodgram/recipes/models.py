from django.core.validators import MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class Ingredient(models.Model):
    """Модель ингредиентов."""

    name = models.CharField('Название', max_length=100, db_index=True)
    measurement_unit = models.CharField('Единица измерения', max_length=50)

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Tag(models.Model):
    """Модель тегов."""

    name = models.CharField('Название', unique=True, max_length=100)
    slug = models.SlugField('Слаг', unique=True, max_length=100)

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField('Название', max_length=256, db_index=True)
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
            models.UniqueConstraint(fields=['recipe', 'ingredient'], name='unique_recipe_ingredient')
        ]

    def __str__(self):
        return f'{self.ingredient.name} в {self.recipe.name}: {self.amount} {self.ingredient.measurement_unit}'


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
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_favorite')
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
            models.UniqueConstraint(fields=['user', 'recipe'], name='unique_shopping_cart')
        ]
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'

    def __str__(self):
        return f'{self.user} добавил "{self.recipe}" в свою корзину'
