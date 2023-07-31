from django.urls import include, path

from rest_framework.routers import DefaultRouter

from .views import UserViewSet, IngredientViewSet, RecipeViewSet

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet, basename='users')
router_v1.register('ingredients', IngredientViewSet, basename='ingridients')
router_v1.register('recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router_v1.urls)),
    path('auth/', include('djoser.urls.authtoken')),
]
