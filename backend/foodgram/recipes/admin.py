from django import forms
from django.contrib import admin

from . import models


class IngredientsInlineFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        super().clean()
        count = 0
        for form in self.forms:
            if not form.cleaned_data.get('DELETE', False):
                count += 1
        if count < 1:
            raise forms.ValidationError('Нельзя удалить все ингредиенты.'
                                        'Добавьте хотя бы один ингредиент.',
                                        code='no_ingredients')


class RecipeIngredientInline(admin.TabularInline):
    model = models.RecipeIngredient
    formset = IngredientsInlineFormset


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug')
    empty_value_display = 'пусто'


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'in_favorites')
    list_editable = ('name',)
    readonly_fields = ('in_favorites', )
    list_filter = ('tags',)
    inlines = [RecipeIngredientInline, ]
    search_fields = ('name', 'author', )
    empty_value_display = 'пусто'

    @admin.display(description='В избранном')
    def in_favorites(self, obj):
        return obj.favorites.count()


@admin.register(models.RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')


@admin.register(models.ShoppingList)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    list_editable = ('user', 'recipe')
