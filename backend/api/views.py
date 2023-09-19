from django.db.models import F, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from recipes.models import (
    Cart,
    Favorite,
    Ingredient,
    IngredientAmount,
    Recipe,
    Tag
)
from .filters import RecipeFilterSet
from .paginator import LimitedPagination
from .permissions import AdminOrReadOnly, AuthorOrAdminOrReadOnly
from .serializers import (
    CartSerializer,
    FavoriteSerializer,
    IngredientSerializer,
    RecipeCreateSerializer,
    RecipeMiniSerializer,
    RecipeSerializer,
    TagSerializer
)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для ингридиента"""

    # queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None

    def get_queryset(self):
        query = self.request.query_params.get('name', '')
        queryset = Ingredient.objects.filter(name__icontains=query)
        return queryset


class TagBaseViewSet(
    viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin
):
    """Базовый вьюсет для работы с Тэгами"""


class TagViewSet(TagBaseViewSet):
    """Вьюсет для работы с Тэгами"""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminOrReadOnly,)
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    """Вьюсет для работы с рецептами"""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (AuthorOrAdminOrReadOnly,)
    pagination_class = LimitedPagination
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilterSet
    filterset_class = RecipeFilterSet

    def get_serializer_class(self):
        if self.action in ("create", "partial_update"):
            return RecipeCreateSerializer
        if self.action in ("favorite", "shopping_cart"):
            return RecipeMiniSerializer
        return RecipeSerializer

    def get_queryset(self):
        user_id = self.request.user.pk
        return Recipe.objects.add_annotations(user_id)

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[
            AuthorOrAdminOrReadOnly,
        ],
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {"user": request.user.pk, "recipe": recipe.pk}
        serializer = FavoriteSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @favorite.mapping.delete
    def favorite_delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        Favorite.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(
            "Рецепт успешно удален", status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=True,
        methods=["POST"],
        permission_classes=[
            AuthorOrAdminOrReadOnly,
        ],
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        data = {"user": request.user.pk, "recipe": recipe.pk}
        serializer = CartSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        serializer = self.get_serializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @shopping_cart.mapping.delete
    def cart_delete(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)
        Cart.objects.filter(user=request.user, recipe=recipe).delete()
        return Response(
            "Рецепт успешно удален", status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False, methods=["GET"], permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        ingredients = (
            IngredientAmount.objects.filter(recipe__cart__user=request.user)
            .values(
                name=F("ingredient__name"),
                measurement_unit=F("ingredient__measurement_unit"),
            )
            .annotate(amount=Sum("amount"))
        )
        shopping_list = []
        for ingr in ingredients:
            if ingr["name"] in [item.split(" ")[0] for item in shopping_list]:
                for item in shopping_list:
                    if item.split(" ")[0] == ingr["name"]:
                        parts = item.split(" ")
                        existing_amount = int(parts[1])
                        new_amount = int(ingr["amount"])
                        updated_amount = existing_amount + new_amount
                        parts[1] = str(updated_amount)
                        updated_item = " ".join(parts)
                        shopping_list.remove(item)
                        shopping_list.append(updated_item)
                        break
            else:
                shopping_list.append(
                    f'{ingr["name"]} '
                    f'{ingr["amount"]} '
                    f'{ingr["measurement_unit"]}'
                )
        if shopping_list:
            shopping_list_text = (
                f"Список покупок {self.request.user}:\n\n"
                + "\n".join(shopping_list)
            )
            filename = f"{self.request.user.username}_shopping_list.txt"
            with open(filename, "w", encoding="utf-8") as file:
                file.write(shopping_list_text)
            response = HttpResponse(
                open(filename, "rb").read(), content_type="text/plain"
            )
            response[
                "Content-Disposition"
            ] = f'attachment; filename="{filename}"'
            return response
