from django.urls import path, include
from rest_framework import routers
from .views import user_views, recipes_views


router = routers.DefaultRouter()
router.register(r'users', user_views.CustomUserViewSet, basename='users')
router.register(r'tags', recipes_views.TagViewSet, basename='tags')
router.register(r'ingredients', recipes_views.IngredientViewSet, basename='ingredients')
router.register(r'recipes', recipes_views.RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
