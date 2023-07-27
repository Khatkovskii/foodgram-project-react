import os
from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    '''Отображение пользователей в админке'''
    list_display = ('username', 'first_name', 'last_name', 'email', 'role')
    list_filter = ('email', 'role')
    empty_value_display = 'пусто'
