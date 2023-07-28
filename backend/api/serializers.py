from django.contrib.auth.password_validation import validate_password

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import User


class UserCreateSerializer(UserCreateSerializer):
    '''Создание нового пользователя'''
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'password')
        
    def validate_password(self, value):
        validate_password(value)
        return value
    
    def validate(self, data):
        '''Проверка данных'''
        username = data.get('username')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        forbidden_username = ['me', 'Me', 'ME']
        if self.initial_data.get('username') in forbidden_username:
            raise serializers.ValidationError(
                f'username:{username} запрещен к использованию!'
            )
        if not first_name:
            raise serializers.ValidationError(
                {'Это поле обязательно'}
            )
        if not last_name:
            raise serializers.ValidationError(
                {'Это поле обязательно'}
            )
        return data
    
class UserReadSerializer(UserSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'username', 'first_name', 'last_name')
        