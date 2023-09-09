from rest_framework import serializers
from django.db import transaction
from drf_extra_fields.fields import Base64ImageField
from users.models import CustomUser, AuthorSubscription
from recipes.models import (
    Tag, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Favorite
)
from djoser.serializers import UserSerializer, UserCreateSerializer


RECIPES_LIMIT: int = 2


class CustomUserSerializer(UserSerializer):
    """
    Сериализатор пользователей.

    Сериализатор для отображения и управления данными пользователей.

    Атрибуты:
        - `model` `(Model)`: Модель CustomUser.
        - `fields` `(tuple)`: Поля, которые должны быть сериализованы.

    Поля:
        - `email` `(str)`: Email пользователя.
        - `id` `(int)`: Уникальный идентификатор пользователя.
        - `username` `(str)`: Имя пользователя.
        - `first_name` `(str)`: Имя пользователя.
        - `last_name` `(str)`: Фамилия пользователя.
        - `is_subscribed` `(bool)`: Флаг, указывающий,
            подписан ли пользователь на авторов.

    Методы:
        - `get_is_subscribed`:
            Получить информацию о подписке пользователя.

        Аргументы:
            - `object` `(CustomUser)`: Объект пользователя.

        Возвращает:
            - `bool`: True, если пользователь подписан на авторов, иначе False.
    """

    is_subscribed = serializers.SerializerMethodField(read_only=True)

    def get_is_subscribed(self, object):
        request = self.context.get('request')
        return (
            request is not None
            and not request.user.is_anonymous
            and object.author.filter(subscriber=request.user).exists()
        )

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        )


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор создания пользователей.

    Сериализатор для создания новых пользователей.

    Атрибуты:
        - `model` `(Model)`: Модель CustomUser.
        - `fields` `(tuple)`: Поля, которые должны быть сериализованы.
        - `extra_kwargs` `(dict)`: Дополнительные параметры для полей.

    Поля:
        - `email` `(str)`: Email пользователя.
        - `id` `(int)`: Уникальный идентификатор пользователя.
        - `username` `(str)`: Имя пользователя.
        - `first_name` `(str)`: Имя пользователя.
        - `last_name` `(str)`: Фамилия пользователя.
        - `password` `(str)`: Пароль пользователя.

    Методы:
        - `validate`:
            Валидация данных пользователя при создании.

        Аргументы:
            - `data` `(dict)`: Входные данные пользователя.

        Возвращает:
            - `dict`: Проверенные данные пользователя.

        Исключения:
            - `serializers.ValidationError`: Если имя пользователя 'me'.
    """

    def validate(self, data):
        if data.get('username') == 'me':
            raise serializers.ValidationError(
                'Использовать имя me запрещено'
            )
        return data

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {'password': {'write_only': True}}


class SubscriptionSerializer(serializers.ModelSerializer):
    """
    Сериализатор подписки на авторов.

    Сериализатор для отображения и управления
        данными подписок пользователей на авторов.

    Атрибуты:
        - `model` `(Model)`: Модель AuthorSubscription.
        - `fields` `(tuple)`: Поля, которые должны быть сериализованы.
    """

    class Meta:
        model = AuthorSubscription
        fields = (
            'subscriber',
            'author'
        )


class SubscriptionShowSerializer(CustomUserSerializer):
    """
    Сериализатор для отображения подписок пользователя.

    Сериализатор для отображения данных о
        подписках пользователя на авторов и их рецепты.

    Атрибуты:
        - `model` `(Model)`: Модель CustomUser.
        - `fields` `(tuple)`: Поля, которые должны быть сериализованы.

    Поля:
        - `email` `(str)`: Email пользователя.
        - `id` `(int)`: Уникальный идентификатор пользователя.
        - `username` `(str)`: Имя пользователя.
        - `first_name` `(str)`: Имя пользователя.
        - `last_name` `(str)`: Фамилия пользователя.
        - `is_subscribed` `(bool)`:
            Флаг, указывающий, подписан ли пользователь на авторов.
        - `recipes` `(list)`:
            Список рецептов авторов, на которых подписан пользователь.
        - `recipes_count` `(int)`:
            Количество рецептов авторов, на которых подписан пользователь.

    Методы:
        - `get_recipes`:
            Получить список рецептов авторов, на которых подписан пользователь.

        Аргументы:
            - `object` `(CustomUser)`: Объект пользователя.

        Возвращает:
            - `list`: Список рецептов авторов.

        - `get_recipes_count`:
            Получить количество рецептов авторов,
            на которых подписан пользователь.

        Аргументы:
            - `object` `(CustomUser)`: Объект пользователя.

        Возвращает:
            - `int`: Количество рецептов авторов.
    """

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    def get_recipes(self, object):
        author_recipes = object.recipes.all()[:RECIPES_LIMIT]
        return RecipeSerializer(
            author_recipes, many=True
        ).data

    def get_recipes_count(self, object):
        return object.recipes.count()

    class Meta:
        model = CustomUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        )


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор тегов.

    Сериализатор для отображения и управления данными тегов.

    Атрибуты:
        - `model` `(Model)`: Модель Tag.
        - `fields` `(tuple)`: Поля, которые должны быть сериализованы.
    """
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug'
        )


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиентов.

    Сериализатор для отображения и управления данными ингредиентов.

    Атрибуты:
        - `model` `(Model)`: Модель Ingredient.
        - `fields` `(tuple)`: Поля, которые должны быть сериализованы.
    """
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit'
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount'
        )


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиентов рецепта.

    Сериализатор для отображения и управления данными ингредиентов рецепта.

    Атрибуты:
        - `model` `(Model)`: Модель RecipeIngredient.
        - `fields` `(tuple)`: Поля, которые должны быть сериализованы.

    Поля:
        - `id` `(int)`: Уникальный идентификатор ингредиента.
        - `name` `(str)`: Название ингредиента.
        - `measurement_unit` `(str)`: Единица измерения ингредиента.
        - `amount` `(float)`: Количество ингредиента в рецепте.
    """
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects.all())
    amount = serializers.IntegerField(
        required=True,
        write_only=True,
        min_value=1,
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецептов.

    Сериализатор для отображения и управления данными рецептов.

    Атрибуты:
        - `model` `(Model)`: Модель Recipe.
        - `fields` `(tuple)`: Поля, которые должны быть сериализованы.

    Поля:
        - `tags` `(list)`: Список тегов, связанных с рецептом.
        - `author` `(CustomUserSerializer)`:
            Сериализатор пользователя-автора рецепта.
        - `ingredients` `(list)`: Список ингредиентов рецепта.
        - `image` `(str)`: Изображение рецепта в формате base64.
        - `is_in_shopping_cart` `(bool)`:
            Флаг, указывающий, есть ли рецепт в списке пользователя.
        - `is_favorited` `(bool)`:
            Флаг, указывающий, добавлен ли рецепт в избранное пользователя.

    Методы:
        - `get_is_in_shopping_cart`:
            Получить информацию о наличии рецепта в списке пользователя.

        Аргументы:
            - `object` `(Recipe)`: Объект рецепта.

        Возвращает:
            - `bool`:
                True, если рецепт находится
                в списке пользователя, иначе False.

        - `get_is_favorited`:
            Получить информацию о наличии рецепта в избранном пользователя.

        Аргументы:
            - `object` `(Recipe)`: Объект рецепта.

        Возвращает:
            - `bool`:
                True, если рецепт находится в
                избранном пользователя, иначе False.
    """
    tags = TagSerializer(many=True, read_only=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        read_only=True,
        source='recipeingredient_set'
    )
    image = serializers.ReadOnlyField(source='image.url')
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    is_favorited = serializers.SerializerMethodField(read_only=True)

    def get_is_in_shopping_cart(self, object):
        request = self.context.get('request')
        return (
            request is not None
            and not request.user.is_anonymous
            and request.user.shopping_cart.filter(recipe=object).exists()
        )

    def get_is_favorited(self, object):
        request = self.context.get('request')
        return (
            request is not None
            and not request.user.is_anonymous
            and request.user.favoriting.filter(recipe=object).exists()
        )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'image',
            'is_in_shopping_cart',
            'is_favorited',
            'name',
            'text',
            'cooking_time',
            'pub_date'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания рецептов.

    Сериализатор для создания новых рецептов.

    Атрибуты:
        - `model` `(Model)`: Модель Recipe.
        - `fields` `(tuple)`: Поля, которые должны быть сериализованы.

    Поля:
        - `tags` `(list)`: Список тегов, связанных с рецептом.
        - `ingredients` `(list)`: Список ингредиентов рецепта.
        - `author` `(CustomUserSerializer)`:
            Сериализатор пользователя-автора рецепта.
        - `image` `(str)`: Изображение рецепта в формате base64.

    Методы:
        - `add_ingredients`:
            Добавить ингредиенты к рецепту.

        Аргументы:
            - `ingredients_data` `(list)`: Данные ингредиентов.
            - `recipe` `(Recipe)`: Объект рецепта.

        - `create`:
            Создать новый рецепт.

        Аргументы:
            - `validated_data` `(dict)`: Проверенные данные рецепта.

        Возвращает:
            - `Recipe`: Созданный объект рецепта.

        - `update`:
            Обновить существующий рецепт.

        Аргументы:
            - `instance` `(Recipe)`: Существующий объект рецепта.
            - `validated_data` `(dict)`: Проверенные данные рецепта.

        Возвращает:
            - `Recipe`: Обновленный объект рецепта.
    """
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        required=True,
        queryset=Tag.objects.all())
    ingredients = RecipeIngredientCreateSerializer(
        many=True,
        required=True)
    author = CustomUserSerializer(read_only=True)
    image = Base64ImageField(required=False)

    @staticmethod
    def __add_ingredients(ingredients_data, recipe):

        RecipeIngredient.objects.bulk_create([
            RecipeIngredient(
                ingredient=ingredient.get('id'),
                recipe=recipe,
                amount=ingredient.get('amount')
            )
            for ingredient in ingredients_data
        ])

    @transaction.atomic
    def create(self, validated_data):
        author = self.context.get('request').user
        tags_data = validated_data.pop('tags')
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags_data)
        self.__add_ingredients(ingredients_data, recipe)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        recipe = instance
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.name)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        instance.tags.clear()
        instance.ingredients.clear()
        tags_data = validated_data.get('tags')
        instance.tags.set(tags_data)
        ingredients_data = validated_data.get('ingredients')
        RecipeIngredient.objects.filter(recipe=recipe).delete()
        self.__add_ingredients(ingredients_data, recipe)
        instance.save()
        return instance

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'ingredients',
            'author',
            'image',
            'name',
            'text',
            'cooking_time',
            'pub_date'
        )


class ShoppingCartSerializer(serializers.ModelSerializer):
    """
    Сериализатор списка покупок.

    Сериализатор для отображения и управления
    данными списка покупок пользователей.

    Атрибуты:
        - `model` `(Model)`: Модель ShoppingCart.
        - `fields` `(tuple)`: Поля, которые должны быть сериализованы.
    """
    class Meta:
        model = ShoppingCart
        fields = (
            'user',
            'recipe'
        )


class FavoriteSerializer(serializers.ModelSerializer):
    """
    Сериализатор избранных рецептов.

    Сериализатор для отображения и управления
    данными избранных рецептов пользователей.

    Атрибуты:
        - `model` `(Model)`: Модель Favorite.
        - `fields` `(tuple)`: Поля, которые должны быть сериализованы.
    """
    class Meta:
        model = Favorite
        fields = (
            'user',
            'recipe',
            'added_at'
        )
