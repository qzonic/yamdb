from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    TitleViewSet,
    CategoryViewSet,
    GenreViewSet,
    RegisterAPIView,
    TokenAPIView,
    UserViewSet,
    ReviewViewSet,
    CommentViewSet
)


app_name = 'api'

router = DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'titles', TitleViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'genres', GenreViewSet)
router.register(
    r'titles/(?P<title_id>\d+)/reviews',
    ReviewViewSet,
    basename='reviews'
)
router.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentViewSet,
    basename='comments'
)
router.register(r"users", UserViewSet)


urlpatterns = [
    path('v1/auth/signup/', RegisterAPIView.as_view()),
    path('v1/auth/token/', TokenAPIView.as_view()),
    path('v1/', include(router.urls)),
]
