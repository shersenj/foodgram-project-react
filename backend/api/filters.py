from django_filters import rest_framework as filters
from recipes.models import Recipe, Ingredient


class RecipeFilter(filters.FilterSet):
    """
    Фильтры для рецептов.

    Методы:
        - `get_is_favorited`:
            Получает фильтрованный `QuerySet`
            для рецептов в избранном или не в избранном.
        - `get_is_in_shopping_cart`:
            Получает фильтрованный `QuerySet`
            для рецептов в списке покупок или не в нём.

    Атрибуты:
        - `tags` `(AllValuesMultipleFilter)`: Фильтр по тегам рецептов.
        - `is_favorited` `(BooleanFilter)`: Фильтр по наличию в избранном.
        - `is_in_shopping_cart` `(BooleanFilter)`:
            Фильтр по наличию в корзине покупок.
        - `author` `(AllValuesMultipleFilter)`: Фильтр по автору рецепта.

    Meta:
        - `model` `(Model)`: Модель, к которой применяются фильтры.
        - `fields` `(tuple)`: Поля модели, по которым можно фильтровать.
    """

    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    author = filters.AllValuesMultipleFilter(field_name='author__id')

    class Meta:
        model = Recipe
        fields = ('tags', 'author', 'is_favorited', 'is_in_shopping_cart')

    def get_is_favorited(self, queryset, name, value):
        """
        Получает фильтрованный `QuerySet`
            для рецептов в избранном или не в избранном.

        Аргументы:
            - `queryset` `(QuerySet)`: Исходный QuerySet рецептов.
            - `name` `(str)`: Имя поля фильтра.
            - `value` `(bool)`: Значение фильтра
            (`True`, если в избранном, `False` иначе).

        Возвращает:
            - `QuerySet`: Фильтрованный QuerySet рецептов.
        """
        if value:
            return queryset.filter(favoriting__user=self.request.user)
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        """
        Получает фильтрованный `QuerySet`
            для рецептов в списке покупок или не в нём.

        Аргументы:
            - `queryset` `(QuerySet)`: Исходный `QuerySet` рецептов.
            - `name` `(str)`: Имя поля фильтра.
            - `value` `(bool)`:
                Значение фильтра (`True`, если в корзине, `False` иначе).

        Возвращает:
            QuerySet: Фильтрованный QuerySet рецептов.
        """
        if value:
            return queryset.filter(shopping_cart__user=self.request.user)
        return queryset


class IngredientSearchFilter(filters.FilterSet):
    """
    Фильтр для поиска ингредиентов по имени.

    Атрибуты:
        - `name` `(CharFilter)`:
            Фильтр по начальным символам имени ингредиента.

    Meta:
        - `model` `(Model)`: Модель, к которой применяется фильтр.
        - `fields` `(tuple)`: Поля модели, по которым можно фильтровать.
    """
    name = filters.CharFilter(lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ('name', )
