from django.db import models
from django.db.models import UniqueConstraint
from users.models import CustomUser
from .validators import (
    validate_hex_color,
    validate_slug,
    validate_positive_integer,
    validate_name,
)


class Tag(models.Model):
    """
    Модель для хранения тегов, которые могут быть присвоены рецептам.

    Поля:
    - `name`: Название тега.
    - `color`: Цвет тега (в формате HEX).
    - `slug`: Уникальный идентификатор тега.

    """
    name = models.CharField(
        max_length=200,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Название',
        validators=[validate_name]
    )
    color = models.CharField(
        max_length=7,
        blank=False,
        null=False,
        verbose_name='Цвет',
        validators=[validate_hex_color]
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        blank=False,
        null=False,
        verbose_name='Slug',
        validators=[validate_slug]
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ('name',)

    def __str__(self):
        return self.slug


class Ingredient(models.Model):
    """
    Модель для хранения ингредиентов,
        которые могут быть использованы в рецептах.

    Поля:
    - `name`: Название ингредиента.
    - `measurement_unit`: Единицы измерения ингредиента.

    """
    name = models.CharField(
        max_length=100,
        blank=False,
        null=False,
        verbose_name='Название'
    )
    measurement_unit = models.CharField(
        max_length=20,
        blank=False,
        null=False,
        verbose_name='Единицы измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """
    Модель для хранения рецептов блюд.

    Поля:
    - `author`: Автор рецепта (ссылка на модель CustomUser).
    - `name`: Название рецепта.
    - `image`: Картинка блюда.
    - `text`: Описание рецепта.
    - `ingredients`: Связь многие-ко-многим с моделью Ingredient
        через промежуточную модель RecipeIngredient.
    - `tags`: Связь многие-ко-многим с моделью Tag.
    - `cooking_time`: Время приготовления (в минутах).
    - `pub_date`: Дата публикации рецепта.

    """
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='recipes',
        blank=False,
        null=False,
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        blank=False,
        null=False,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/',
        blank=False,
        null=False,
        verbose_name='Картинка'
    )
    text = models.TextField(
        blank=False,
        null=False,
        verbose_name='Описание'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        through='RecipeIngredient',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        Tag,
        related_name='recipes',
        blank=False,
        verbose_name='Теги'
    )
    cooking_time = models.PositiveIntegerField(
        blank=False,
        null=False,
        verbose_name='Время приготовления (минуты)',
        validators=[validate_positive_integer]
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='Дата публикации'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """
    Промежуточная модель для хранения информации об ингредиентах в рецептах.

    Поля:
    - `recipe`: Рецепт (ссылка на модель Recipe).
    - `ingredient`: Ингредиент (ссылка на модель Ingredient).
    - `amount`: Количество ингредиента в рецепте.

    """
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент'
    )
    amount = models.PositiveIntegerField(
        validators=[validate_positive_integer],
        verbose_name='Количество'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]
        verbose_name = 'Ингредиент для рецепта'
        verbose_name_plural = 'Ингредиенты для рецепта'
        ordering = ('recipe',)

    def __str__(self):
        return (
            f'{self.amount} '
            f'{self.ingredient} для {self.recipe}'
        )


class Favorite(models.Model):
    """
    Модель для хранения избранных рецептов пользователей.

    Поля:
    - `user`: Пользователь (ссылка на модель CustomUser).
    - `recipe`: Рецепт (ссылка на модель Recipe).
    - `added_at`: Дата добавления рецепта в избранное.

    """
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='favoriting',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favoriting',
        verbose_name='Рецепт'
    )
    added_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe'
            )
        ]
        verbose_name = 'Избранный рецепт'
        verbose_name_plural = 'Избранные рецепты'

    def __str__(self):
        return f'{self.user.username} - {self.recipe.name}'


class ShoppingCart(models.Model):
    """
    Модель для хранения рецептов в списке покупок пользователей.

    Поля:
    - `user`: Пользователь (ссылка на модель CustomUser).
    - `recipe`: Рецепт (ссылка на модель Recipe).

    """
    user = models.ForeignKey(
        CustomUser,
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
            UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_user_recipe_in_cart'
            )
        ]
        verbose_name = 'Рецепт для списка покупок'
        verbose_name_plural = 'Рецепты для списка покупок'
        ordering = ('user',)

    def __str__(self):
        return (f'{self.recipe} в списке покупок у {self.user}')
