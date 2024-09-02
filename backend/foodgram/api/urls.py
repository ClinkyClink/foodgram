from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import CustomUserViewSet

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register(r'ingredients', IngredientViewSet, basename='ingredient')
v1_router.register(r'tags', TagViewSet, basename='tag')
v1_router.register(r'recipes', RecipeViewSet, basename='recipe')
v1_router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('v1/auth/', include('djoser.urls')),
    path('v1/auth/', include('djoser.urls.authtoken')),
    path('v1/', include(v1_router.urls)),
]