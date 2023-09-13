from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import IngredientViewSet, RecipeViewSet, TagViewSet

router_v1 = DefaultRouter()

router_v1.register("ingredients", IngredientViewSet, basename="ingridients")
router_v1.register("recipes", RecipeViewSet, basename="recipes")
router_v1.register("tags", TagViewSet, basename="tags")

urlpatterns = [
    path("", include(router_v1.urls)),
    # path("auth/", include("djoser.urls.authtoken")),
]
