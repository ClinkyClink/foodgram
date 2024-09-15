from django.contrib import admin

from . import models


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


class RecipeIngredientInline(admin.TabularInline):
    model = models.RecipeIngredient
    extra = 1
    fields = ('ingredient', 'amount')


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'in_favorites')
    list_editable = ('name',)
    readonly_fields = ('in_favorites',)
    list_filter = ('tags',)
    search_fields = ('name', 'author',)
    empty_value_display = 'пусто'
    inlines = [RecipeIngredientInline]

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
