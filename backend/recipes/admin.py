from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin

from .models import Ingredient, Tag, Recipe, IngredientAmount, Favorite, Cart
from api.params import MIN_AMOUNT, MAX_AMOUNT


@admin.register(Ingredient)
class IngredientAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ("name", "measurement_unit")
    search_fields = ("name", "measurement_unit")
    list_filter = ("name",)
    save_on_top = True
    empty_value_display = "---"


class IngredientAmountInline(admin.TabularInline):
    model = IngredientAmount
    min_num = MIN_AMOUNT
    max_num = MAX_AMOUNT


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name",)
    search_fields = ("name",)
    list_filter = ("name",)
    empty_value_display = "---"


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ("author", "name", "cooking_time")
    search_fields = ("name", "author", "tags")
    list_filter = ("name", "author", "tags")
    inlines = (IngredientAmountInline,)
    empty_value_display = "---"


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
    search_fields = ("user",)
    list_filter = ("user",)
    empty_value_display = "---"


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "recipe")
    search_fields = ("user",)
    list_filter = ("user",)
    empty_value_display = "---"
