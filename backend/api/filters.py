from django.contrib.auth import get_user_model
from django_filters import FilterSet, filters

from recipes.models import Recipe, Tag

UserModel = get_user_model()


class RecipeFilterSet(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name="tags__slug",
        queryset=Tag.objects.all(),
        to_field_name="slug",
    )
    author = filters.ModelChoiceFilter(queryset=UserModel.objects.all())
    is_favorited = filters.NumberFilter(method="get_is_favorited")
    is_in_shopping_cart = filters.NumberFilter(
        method="get_is_in_shopping_cart"
    )

    class Meta:
        model = Recipe
        fields = ("tags", "author", "is_favorited", "is_in_shopping_cart")

    def get_is_favorited(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                favorite__user=self.request.user,
                is_favorited=True,
            )
        return queryset

    def get_is_in_shopping_cart(self, queryset, name, value):
        if value and self.request.user.is_authenticated:
            return queryset.filter(
                cart__user=self.request.user,
                is_in_shopping_cart=True,
            )
        return queryset
