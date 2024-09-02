from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet
from users.views import CustomUserViewSet

app_name = 'api'

v1_router = DefaultRouter()

v1_router.register(r'ingredients', IngredientViewSet)
v1_router.register(r'tags', TagViewSet)
v1_router.register(r'recipes', RecipeViewSet)
v1_router.register(r'users', CustomUserViewSet)

urlpatterns = [
    path('v1/', include(v1_router.urls)),
    path('v1/', include('djoser.urls')),
    path('v1/', include('djoser.urls.authtoken')),
]