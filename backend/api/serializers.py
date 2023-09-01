from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinValueValidator, MaxValueValidator
from drf_extra_fields.fields import Base64ImageField

from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from users.models import User
from recipes.models import Recipe, Ingredient, IngredientAmount, Tag, Favorite, Cart
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


class SetPasswordSerializer(serializers.Serializer):
    '''Сериализатор изменения пароля'''
    current_password = serializers.CharField()
    new_password = serializers.CharField()
    
    def validate_new_password(self, value):
        validate_password(value)
        return value
    
    def update(self, instance, validated_data):
        current_password = validated_data.get('current_password')
        new_password = validated_data.get('new_password')
        if not instance.check_password(current_password):
            raise serializers.ValidationError(
                {
                    'current_password': 'Пароль неверный'
                }
            )
        if current_password == new_password:
            raise serializers.ValidationError(
                {
                    'new_password': 'Новый пароль должен отличаться'
                                    'от предидущего'
                }
            )
        instance.set_password(new_password)
        instance.save()
        return validated_data


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
    measurement_unit = serializers.CharField(
        source='ingredient.measurement_unit',
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
        fields = ('id', 'name', 'measurement_unit', 'amount')


class TagSerializer(serializers.ModelSerializer):
    '''Сериализация тегов'''
    
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ('__all__',)


class RecipeSerializer(serializers.ModelSerializer):
    '''Сериализатор рецептов'''
    author = UserReadSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
         many=True,
         source='ingredients_amount'
    )
    image = Base64ImageField(required=False, allow_null=True)
    tags = TagSerializer(read_only=True, many=True)
    # is_favorited = serializers.BooleanField(read_only=True)
    # is_in_shopping_cart = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'name',
            'image', 'text', 'tags', 'cooking_time',
        )


class RecipeCreateSerializer(RecipeSerializer):
    '''Сериализатор создания и обновления рецепта'''
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        many=True
    )
    
    class Meta:
        model = Recipe
        fields = (
            'id', 'author', 'ingredients', 'name', 'text', 'image',
            'tags', 'cooking_time'
        )
    
    @staticmethod
    def ingredient_save(recipe, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            curent_ingredient = ingredient['ingredient']['id']
            curent_amount = ingredient.get('amount')
            ingredients_list.append(IngredientAmount(
                recipe=recipe,
                ingredient=curent_ingredient,
                amount=curent_amount
            ))
        IngredientAmount.objects.filter(recipe=recipe).delete()
        IngredientAmount.objects.bulk_create(ingredients_list)
    
    def create(self, validated_data):
        author = self.context.get('request').user
        ingredients = validated_data.pop('ingredients_amount')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.ingredient_save(recipe, ingredients)
        recipe.tags.add(*tags)
        return recipe
    
    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.image = validated_data.get('image', instance.image)
        instance.cooking_time = validated_data.get('cooking_time', instance.cooking_time)
        tags = validated_data.get('tags')
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.get('ingredients_amount')
        if ingredients is not None:
            IngredientAmount.objects.filter(recipe=instance).delete()
            self.ingredient_save(instance, ingredients)
        instance.save()
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    '''Сериализатор избранных рецептов'''
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в избранном',
            )
        ]

class RecipeMiniSerializer(serializers.ModelSerializer):
    '''Мини сериалитор для добавления рецепта в избранное'''
    
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CartSerializer(serializers.ModelSerializer):
    '''Сериализатор корзины покупок'''
    user = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all()
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all()
    )
    
    class Meta:
        model = Cart
        fields = ('user', 'recipe')
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=('user', 'recipe'),
                message='Рецепт уже в корзине'
            )
        ]