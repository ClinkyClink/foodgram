from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import CustomUserViewSet
from .views import IngredientViewSet, RecipeViewSet, TagViewSet, get_short_link

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register(r'ingredients', IngredientViewSet, basename='ingredient')
v1_router.register(r'tags', TagViewSet, basename='tag')
v1_router.register(r'recipes', RecipeViewSet, basename='recipe')
v1_router.register(r'users', CustomUserViewSet, basename='users')

urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('recipes/<int:recipe_id>/get-link/', get_short_link, name='get-link'),
    path('', include(v1_router.urls)),
]
