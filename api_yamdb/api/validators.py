from rest_framework.validators import ValidationError


def validate_name(value, length):
    if len(value) > length:
        raise ValidationError(
            f'Длина поля не должна превышать {length}'
        )
    return value
