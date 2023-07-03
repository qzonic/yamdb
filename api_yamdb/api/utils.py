from uuid import uuid4

from django.core.mail import send_mail
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken


def generate():
    """ Генерирует уникальную строку """

    return str(uuid4())


def create_token(user):
    """ Создает токен для пользователя """

    token = RefreshToken.for_user(user)
    return str(token.access_token)


def send_confirmation_code(email, confirmation_code):
    """ Отправляет код на почту """

    send_mail(
        'Проверочный код',
        confirmation_code,
        settings.EMAIL,
        [email]
    )
