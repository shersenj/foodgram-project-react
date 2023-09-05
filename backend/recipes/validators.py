from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator, MinValueValidator


def validate_hex_color(value):
    regex_validator = RegexValidator(
        regex=r'^#[0-9a-fA-F]{6}$',
        message='Цвет должен быть в формате HEX (например, "#RRGGBB").',
    )
    try:
        regex_validator(value)
    except ValidationError as e:
        raise ValidationError(e.message)


def validate_slug(value):
    regex_validator = RegexValidator(
        regex=r'^[a-zA-Z0-9_]+$',
        message=(
            'Slug тега может содержать только'
            'буквы, цифры, подчеркивания и дефисы.'
        ),
    )
    try:
        regex_validator(value)
    except ValidationError as e:
        raise ValidationError(e.message)


def validate_positive_integer(value):
    min_value_validator = MinValueValidator(
        limit_value=1,
        message='Значение должно быть больше 0.',
    )
    try:
        min_value_validator(value)
    except ValidationError as e:
        raise ValidationError(e.message)
