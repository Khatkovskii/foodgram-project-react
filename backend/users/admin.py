from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
        'get_recipe_count',
        'get_follower_count',
        'get_following_count',
        'is_staff'
    )
    list_filter = ('role', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('id',)

    def get_recipe_count(self, obj):
        return obj.recipes.count()
    get_recipe_count.short_description = 'Количество рецептов'

    def get_follower_count(self, obj):
        return obj.follower.count()
    get_follower_count.short_description = 'Количество подписчиков'

    def get_following_count(self, obj):
        return obj.following.count()
    get_following_count.short_description = 'Количество подписок'
