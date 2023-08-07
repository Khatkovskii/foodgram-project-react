from django.contrib import admin

from .models import Ingredient, IngredientAmount, Tag

@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'unit')
    search_fields = ('name', 'unit')
    list_filter = ('name',)
    save_on_top = True
    empty_value_display = '---'

@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '---'