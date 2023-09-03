from recipes.models import (
    Tag, Ingredient, Recipe, ShoppingCart, RecipeIngredient, Favorite
)
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import viewsets, permissions, status
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from api.serializers import (
    TagSerializer, IngredientSerializer,
    RecipeSerializer, RecipeCreateSerializer,
    ShoppingCartSerializer, FavoriteSerializer
)
from ..filters import RecipeFilter, IngredientSearchFilter
from ..utils import create_shopping_cart
from django.db.models import Sum


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Класс представления для просмотра тегов.

    Атрибуты:
        - `queryset` `(QuerySet)`: Запрос для выбора всех объектов Tag.
        - `serializer_class` `(class)`: Класс сериализатора для объектов Tag.
        - `pagination_class` `(class)`: Класс пагинации для списка тегов.
        - `permission_classes` `(tuple)`: Кортеж классов разрешений.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Класс представления для просмотра ингредиентов.

    Атрибуты:
        - `queryset` `(QuerySet)`: Запрос для выбора всех объектов Ingredient.
        - `serializer_class` `(class)`:
            Класс сериализатора для объектов Ingredient.
        - `pagination_class` `(class)`:
            Класс пагинации для списка ингредиентов.
        - `filter_backends` `(tuple)`:
            Кортеж фильтров для применения к запросу.
        - `filterset_class` `(class)`: Класс фильтра для поиска ингредиентов.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientSearchFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Класс представления для просмотра и управления рецептами.

    Методы:
        - `get_serializer_class`:
            Определяет класс сериализатора для метода запроса.
        - `get_shopping_cart`:
            Обрабатывает запрос для добавления
            или удаления рецепта из списка покупок.
        - `download_shopping_cart`:
            Обрабатывает запрос на скачивание списка
            ингредиентов из списка покупок.
        - `get_favorite`:
            Обрабатывает запрос для добавления
            или удаления рецепта из избранного.


    Атрибуты:
        - `queryset` `(QuerySet)`: Запрос для выбора всех объектов Recipe.
        - `filter_backends` `(tuple)`:
            Кортеж фильтров для применения к запросу.
        - `filterset_class` `(class)`: Класс фильтра для поиска рецептов.
    """
    queryset = Recipe.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """
        Определяет класс сериализатора для метода запроса.

        Возвращает:
            - `class`: Класс сериализатора.
        """
        if self.request.method == 'GET':
            return RecipeSerializer
        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='shopping_cart',
        url_name='shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_shopping_cart(self, request, pk=None):
        """
        Обрабатывает запрос для добавления
            или удаления рецепта из списка покупок.

        Аргументы:
            - `request` `(HttpRequest)`: Запрос.
            - `pk` `(int)`: Идентификатор рецепта.

        Возвращает:
            - `Response`: Ответ на запрос.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = ShoppingCartSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            shopping_cart_serializer = RecipeSerializer(recipe)
            return Response(
                shopping_cart_serializer.data, status=status.HTTP_201_CREATED
            )
        shopping_cart_recipe = get_object_or_404(
            ShoppingCart, user=request.user, recipe=recipe
        )
        shopping_cart_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        url_path='download_shopping_cart',
        url_name='download_shopping_cart',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """
        Обрабатывает запрос на скачивание списка
            ингредиентов из списка покупок.

        Аргументы:
            - `request` `(HttpRequest)`: Запрос.

        Возвращает:
            - `Response`: Ответ на запрос с данными для скачивания.
        """
        ingredients_cart = (
            RecipeIngredient.objects.filter(
                recipe__shopping_cart__user=request.user
            ).values(
                'ingredient__name',
                'ingredient__measurement_unit',
            ).order_by(
                'ingredient__name'
            ).annotate(ingredient_value=Sum('amount'))
        )
        return create_shopping_cart(ingredients_cart)

    @action(
        detail=True,
        methods=['post', 'delete'],
        url_path='favorite',
        url_name='favorite',
        permission_classes=(permissions.IsAuthenticated,)
    )
    def get_favorite(self, request, pk):
        """
        Обрабатывает запрос для добавления или удаления рецепта из избранного.

        Аргументы:
            - `request` `(HttpRequest)`: Запрос.
            - `pk` `(int)`: Идентификатор рецепта.

        Возвращает:
            - `Response`: Ответ на запрос.
        """
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'POST':
            serializer = FavoriteSerializer(
                data={'user': request.user.id, 'recipe': recipe.id}
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            favorite_serializer = RecipeSerializer(recipe)
            return Response(
                favorite_serializer.data, status=status.HTTP_201_CREATED
            )
        favorite_recipe = get_object_or_404(
            Favorite, user=request.user, recipe=recipe
        )
        favorite_recipe.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
