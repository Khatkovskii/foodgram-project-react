from django.contrib import admin
from import_export.admin import ImportExportActionModelAdmin

from .models import Ingredient, IngredientAmount, Tag

@admin.register(Ingredient)
class IngredientAdmin(ImportExportActionModelAdmin, admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name', 'measurement_unit')
    list_filter = ('name',)
    save_on_top = True
    empty_value_display = '---'

@admin.register(Tag)
class Tag(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '---'