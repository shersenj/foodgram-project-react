from django.contrib import admin
from .models import (Tag, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Favorite)
from django.utils.safestring import mark_safe


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug')
    search_fields = ('name',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author',
                    'get_total_favorite_count', 'get_ingredients')
    list_filter = ('author', 'name', 'tags')
    filter_horizontal = ('ingredients', 'tags')

    def get_total_favorite_count(self, obj):
        return obj.favoriting.count()

    get_total_favorite_count.short_description = 'Избранное'

    def get_ingredients(self, object):
        """Получает ингредиент или список ингредиентов рецепта."""
        ingredients = '<br>'.join(
            (ingredient.name for ingredient in object.ingredients.all())
        )
        return mark_safe(ingredients)

    get_ingredients.short_description = 'Ингредиенты'


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'ingredient', 'amount', 'get_unit')

    def get_unit(self, obj):
        return obj.ingredient.measurement_unit if obj.ingredient else ''

    get_unit.short_description = 'Единицы измерения'


@admin.register(ShoppingCart)
class ShoppingListItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')


@admin.register(Favorite)
class FavoriteRecipeAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe', 'added_at')
