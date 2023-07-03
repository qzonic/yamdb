from django.utils import timezone
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError

from api.utils import generate


def validate_year(value):
    dt = timezone.now().year
    if value > dt or dt < 0:
        raise ValidationError(
            'Год (%(value)s) не может быть больше текущего',
            params={'value': value},
        )
    return value


class Genre(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=256)
    slug = models.SlugField(unique=True, max_length=50)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField('Название', max_length=256)
    description = models.TextField('Описание')
    year = models.IntegerField(validators=[validate_year])
    pub_date = models.DateTimeField('Дата публикации', auto_now_add=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True,
        blank=False,
        verbose_name="Категория"
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='titles',
        blank=True,
        verbose_name="Жанр"
    )

    def __str__(self):
        return self.name


class User(AbstractUser):
    """ Модель пользователя """

    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    ROLES = (
        (ADMIN, ADMIN),
        (MODERATOR, MODERATOR),
        (USER, USER)
    )
    bio = models.TextField(
        null=True,
        blank=True,
        verbose_name='Биография'
    )
    role = models.CharField(
        max_length=9,
        choices=ROLES,
        default=USER,
        verbose_name='Роль'
    )
    confirmation_code = models.CharField(
        max_length=50,
        default=generate(),
        verbose_name='Код подтверждения'
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='Email'
    )

    @property
    def is_moderator(self):
        return self.role == self.MODERATOR

    @property
    def is_admin(self):
        return self.is_staff or self.role == self.ADMIN

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['username', 'email'],
                name='unique username and email'
            )
        ]


class Review(models.Model):
    """Модель отзывов к произведениям."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Имя пользователя'
    )
    title = models.ForeignKey(
        Title,
        on_delete=models.CASCADE,
        related_name='reviews'
    )
    text = models.TextField(verbose_name='Текст отзыва')
    score = models.PositiveSmallIntegerField(
        validators=[MaxValueValidator(10), MinValueValidator(1)],
        verbose_name='Оценка',
        default=0
    )
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации отзыва',
        auto_now_add=True
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['title', 'author'],
                name='Одно произведение - один отзыв одному автору'
            )
        ]
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text


class Comment(models.Model):
    """Модель комментариев к отзывам."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Имя пользователя'
    )
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(verbose_name='Текст комментария')
    pub_date = models.DateTimeField(
        verbose_name='Дата публикации комментария',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date',)

    def __str__(self):
        return self.text
