from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinValueValidator, MaxValueValidator

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import User
from recipes.models import Recipe, Ingredient, IngredientAmount
from .params import MIN_AMOUNT, MAX_AMOUNT


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


class IngredientSerializer(serializers.ModelSerializer):
    '''Сериализатор для ингредиентов'''
    
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = '__all__',

class IngredientAmountSerializer(serializers.ModelSerializer):
    '''Сериализатор колличества ингридиентов'''
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient.id'
    )
    name = serializers.CharField(
        source='ingredient.name',
        read_only=True
    )
    unit = serializers.CharField(
        source='ingredient.unit',
        read_only=True
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                'Минимальное количество ингридиентов: '
                f'{MIN_AMOUNT}'
            ),
            MaxValueValidator(
                MAX_AMOUNT,
                'Максимальное количество ингридиентов: '
                f'{MAX_AMOUNT}'
            )
        ]
    )
    
    class Meta:
        model = IngredientAmount
        fields = ('id', 'name', 'unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор рецептов'''
    author = UserReadSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
         many=True,
         source='ingredient_amount'
    )
    image = serializers.ImageField(required=False, allow_null=True)
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'name',
            'image', 'description',
        )