import re
from django.db.models import Avg
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from .validators import validate_name
from reviews.models import Genre, Category, Title, User, Review, Comment


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для отзывов к произведениям."""
    author = SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'pub_date')
        read_only_fields = ('pub_date',)

    def validate(self, data):
        """Запрет публицакии только одного отзыва на каждое произведение."""
        if self.context['request'].method != 'POST':
            return data
        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context['request'].user
        review = Review.objects.filter(
            author=author, title=title_id
        )
        if review.exists():
            raise serializers.ValidationError(
                'На каждое произведение можно опубликовать только один отзыв.'
            )
        return data

    def validate_score(self, value):
        """Запрет публикации отзыва с некорректной оценкой."""
        if not 1 <= value <= 10:
            raise serializers.ValidationError(
                'Оценка должна быть в диапазоне от 1 до 10 (целое число).'
            )
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для комментариев к отзывам."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date')
        read_only_fields = ('pub_date',)


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для жанров произведений."""
    class Meta:
        model = Genre
        fields = ('name', 'slug')
        lookup_field = 'slug'


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для категорий произведений."""
    class Meta:
        model = Category
        fields = ('name', 'slug')
        lookup_field = 'slug'


class TitleGetSerializer(serializers.ModelSerializer):
    """Сериализатор для GET запросов произведений."""
    category = CategorySerializer()
    genre = GenreSerializer(many=True)
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        fields = ('id', 'name', 'year', 'rating', 'description', 'genre',
                  'category')

    def get_rating(self, obj):
        rating = obj.reviews.aggregate(Avg('score')).get('score__avg')
        if not rating:
            return rating
        return round(rating, 1)


class TitlePostSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Genre.objects.all(),
        many=True
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre', 'category')


class UserSerializer(serializers.ModelSerializer):
    """ Сериализатор для пользователей """

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'bio',
            'role',
            'confirmation_code'
        )
        extra_kwargs = {
            'confirmation_code': {'write_only': True}
        }

    def validate_first_name(self, value):
        return validate_name(value, 150)

    def validate_last_name(self, value):
        return validate_name(value, 150)

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Пользователь с таким username уже существует'
            )
        pattern = re.compile(r'^[\w.@+-]+')
        if not pattern.match(value):
            raise serializers.ValidationError(
                'Неверный формат поля'
            )
        return validate_name(value, 150)

    def validate_email(self, value):
        return validate_name(value, 254)


class RegisterSerializer(serializers.ModelSerializer):
    """ Сериализатор для решистрации пользователя """

    username = serializers.CharField(
        max_length=150
    )
    email = serializers.EmailField(
        max_length=254
    )

    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Использовать имя "me" в качестве username запрещено'
            )
        pattern = re.compile(r'^[\w.@+-]+')
        if not pattern.match(value):
            raise serializers.ValidationError(
                r'Поле username должно соответсвовать паттерну: ^[\w.@+-]+\z'
            )
        return value


class TokenSerializer(serializers.Serializer):
    """
    Сериализатор для отправки проверочного кода
    и получения jwt-токена
    """

    username = serializers.CharField(
        max_length=128,
    )
    confirmation_code = serializers.CharField(
        max_length=50
    )

    class Meta:
        fields = '__all__'
