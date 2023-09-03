from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import EmailValidator
from django.contrib.auth.validators import UnicodeUsernameValidator


WARNING_MSG_EMAIL = 'Введите корректный адрес электронной почты(mail@mail.ru).'
ERROR_MSG_EMAIL = 'Этот адрес электронной почты уже используется.'
ERROR_MSG_USERNAME = 'Пользователь с таким именем пользователя уже существует.'

custom_username_validator = UnicodeUsernameValidator(
    message='Введите корректное имя пользователя.'
            'Это значение может содержать только буквы,'
            'цифры и символы: @/./+/-/_'
)


class CustomUser(AbstractUser):
    """
    Модель пользовательского аккаунта, расширяющая
    стандартную модель пользователя Django.

    Поля:
    - `email`: Адрес электронной почты пользователя
        (обязательное поле, уникальное).
    - `username`: Имя пользователя
        (обязательное поле, уникальное, подчиняется кастомному валидатору).
    - `first_name`: Имя пользователя.
    - `last_name`: Фамилия пользователя.

    Атрибуты:
    - `USERNAME_FIELD`:
        Поле, используемое для аутентификации пользователя (email).
    - `REQUIRED_FIELDS`: Список полей, необходимых для создания пользователя.

    """
    email = models.EmailField(
        max_length=254,
        validators=[EmailValidator(
            WARNING_MSG_EMAIL)],
        verbose_name='Адрес электронной почты',
        unique=True,
        error_messages={
            'unique': ERROR_MSG_EMAIL},
        blank=False,
        null=False
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        blank=False,
        null=False,
        validators=[custom_username_validator],
        error_messages={
            'unique': ERROR_MSG_USERNAME,
        }
    )
    first_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=150,
        blank=False,
        null=False,
        verbose_name='Фамилия'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    class Meta:
        db_table = 'auth_user'
        ordering = ('id',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


class AuthorSubscription(models.Model):
    """
    Модель подписки пользователя на автора.

    Поля:
    - `subscriber`: Пользователь, который подписывается на автора.
    - `author`: Пользователь, на которого подписываются.

    Атрибуты:
    - `unique_together`:
        Гарантирует уникальность комбинации `subscriber` и `author`.

    """
    subscriber = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriber'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='author'
    )

    class Meta:
        unique_together = ('author', 'subscriber')
        verbose_name = 'Подписка на автора'
        verbose_name_plural = 'Подписки на авторов'

    def __str__(self):
        return f'{self.subscriber} подписан на {self.author}'
