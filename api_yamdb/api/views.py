from django.shortcuts import get_object_or_404
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, filters, viewsets, pagination

from .filters import TitleFilter
from reviews.models import User, Title, Review, Comment, Category, Genre
from .utils import (
    generate,
    send_confirmation_code,
    create_token
)
from .serializers import (
    GenreSerializer,
    CategorySerializer,
    TitleGetSerializer,
    TitlePostSerializer,
    RegisterSerializer,
    UserSerializer,
    TokenSerializer,
    ReviewSerializer,
    CommentSerializer
)
from .permissions import (
    IsAdmin,
    IsAdminOrReadOnly,
    ReviewAndCommentPermission
)


class GenreViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @action(
        detail=False, methods=['delete'],
        url_path=r'(?P<slug>\w+)',
        lookup_field='slug', url_name='category_slug'
    )
    def get_genre(self, request, slug):
        category = self.get_object()
        serializer = CategorySerializer(category)
        category.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class CategoryViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('name',)

    @action(
        detail=False, methods=['delete'],
        url_path=r'(?P<slug>\w+)',
        lookup_field='slug', url_name='category_slug'
    )
    def get_category(self, request, slug):
        category = self.get_object()
        serializer = CategorySerializer(category)
        category.delete()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)


class TitleViewSet(viewsets.ModelViewSet):
    queryset = Title.objects.all()
    permission_classes = (IsAdminOrReadOnly,)
    pagination_class = pagination.LimitOffsetPagination
    filterset_class = TitleFilter

    def get_serializer_class(self):
        if self.request.method in ['POST', 'PUT', 'PATCH']:
            return TitlePostSerializer
        return TitleGetSerializer


class ReviewViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Review."""
    serializer_class = ReviewSerializer
    permission_classes = (ReviewAndCommentPermission,)

    def get_title(self):
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        return Review.objects.filter(title=self.get_title())

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(viewsets.ModelViewSet):
    """Вьюсет для модели Comment."""
    serializer_class = CommentSerializer
    permission_classes = (ReviewAndCommentPermission,)

    def get_review(self):
        return get_object_or_404(Review, id=self.kwargs.get('review_id'))

    def get_queryset(self):
        review_id = self.kwargs.get("review_id")
        title_id = self.kwargs.get("title_id")
        review = get_object_or_404(Review, id=review_id, title=title_id)
        return Comment.objects.filter(review=review)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user, review=self.get_review())


class RegisterAPIView(APIView):
    """ View для регистрации """

    register_serializer = RegisterSerializer
    user_serializer = UserSerializer

    def post(self, request):
        serializer = self.register_serializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        user = User.objects.filter(
            username=username,
            email=email
        ).first()
        if user:
            code = user.confirmation_code
        else:
            code = generate()
            data = {
                'username': username,
                'email': email,
                'confirmation_code': code
            }
            user = self.user_serializer(data=data)
            if user.is_valid():
                user.save()
            else:
                return Response(
                    user.errors,
                    status=status.HTTP_400_BAD_REQUEST)
        send_confirmation_code(email, code)
        return Response(dict(serializer.validated_data))


class TokenAPIView(APIView):
    """ View для создания и отправки токена """

    serializer_class = TokenSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST)
        username = serializer.validated_data.get(
            'username'
        )
        confirmation_code = serializer.validated_data.get(
            'confirmation_code'
        )
        user = get_object_or_404(User, username=username)
        if user.confirmation_code == confirmation_code:
            token = create_token(user)
            data = {
                'token': token
            }
            return Response(data)
        return Response(
            {'error': 'Неверный проверочный код'},
            status=status.HTTP_400_BAD_REQUEST
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet для создания пользователя админом,
    для получчения информации о пользователе по username,
    для редактирования информации о пользователе по username,
    для удаления пользователя по username,
    для получения инофрмации о себе через эндпоинт me/,
    для редактирования инофрмации о себе через эндпоинт me/,
    """

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdmin]
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    http_method_names = ['get', 'post', 'patch', 'delete']

    @action(
        detail=False,
        url_path='me',
        methods=['get', 'patch'],
        permission_classes=[IsAuthenticated]
    )
    def me_get_patch(self, request):
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True
            )
            if serializer.is_valid(raise_exception=True):
                serializer.validated_data['role'] = request.user.role
                serializer.save()
                return Response(serializer.data)
            else:
                return Response(serializer.errors)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
