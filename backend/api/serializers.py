from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import (Cart, Favorite, Ingredient, IngredientAmount,
                            Recipe, Tag)
from users.serializers import UserReadSerializer
from .params import MAX_AMOUNT, MIN_AMOUNT

UserModel = get_user_model()


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор для ингредиентов"""

    class Meta:
        model = Ingredient
        fields = "__all__"
        read_only_fields = ("__all__",)


class IngredientAmountSerializer(serializers.ModelSerializer):
    """Сериализатор колличества ингридиентов"""

    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(), source="ingredient.id"
    )
    name = serializers.CharField(source="ingredient.name", read_only=True)
    measurement_unit = serializers.CharField(
        source="ingredient.measurement_unit", read_only=True
    )
    amount = serializers.IntegerField(
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                "Минимальное количество ингридиентов: " f"{MIN_AMOUNT}",
            ),
            MaxValueValidator(
                MAX_AMOUNT,
                "Максимальное количество ингридиентов: " f"{MAX_AMOUNT}",
            ),
        ]
    )

    class Meta:
        model = IngredientAmount
        fields = ("id", "name", "measurement_unit", "amount")


class TagSerializer(serializers.ModelSerializer):
    """Сериализация тегов"""

    class Meta:
        model = Tag
        fields = "__all__"
        read_only_fields = ("__all__",)


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов"""

    author = UserReadSerializer(read_only=True)
    ingredients = IngredientAmountSerializer(
        many=True, source="ingredients_amount"
    )
    image = Base64ImageField(required=False, allow_null=True)
    tags = TagSerializer(read_only=True, many=True)
    is_favorited = serializers.BooleanField(read_only=True)
    is_in_shopping_cart = serializers.BooleanField(read_only=True)

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "name",
            "is_favorited",
            "is_in_shopping_cart",
            "image",
            "text",
            "tags",
            "cooking_time",
        )


class RecipeCreateSerializer(RecipeSerializer):
    """Сериализатор создания и обновления рецепта"""

    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True
    )

    class Meta:
        model = Recipe
        fields = (
            "id",
            "author",
            "ingredients",
            "name",
            "text",
            "image",
            "tags",
            "cooking_time",
            "is_favorited",
            "is_in_shopping_cart",
        )

    @staticmethod
    def ingredient_save(recipe, ingredients):
        ingredients_list = []
        for ingredient in ingredients:
            curent_ingredient = ingredient["ingredient"]["id"]
            curent_amount = ingredient.get("amount")
            ingredients_list.append(
                IngredientAmount(
                    recipe=recipe,
                    ingredient=curent_ingredient,
                    amount=curent_amount,
                )
            )
        IngredientAmount.objects.filter(recipe=recipe).delete()
        IngredientAmount.objects.bulk_create(ingredients_list)

    def create(self, validated_data):
        author = self.context.get("request").user
        ingredients = validated_data.pop("ingredients_amount")
        tags = validated_data.pop("tags")
        recipe = Recipe.objects.create(author=author, **validated_data)
        self.ingredient_save(recipe, ingredients)
        recipe.tags.add(*tags)
        return recipe

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.text = validated_data.get("text", instance.text)
        instance.image = validated_data.get("image", instance.image)
        instance.cooking_time = validated_data.get(
            "cooking_time", instance.cooking_time
        )
        tags = validated_data.get("tags")
        if tags is not None:
            instance.tags.set(tags)
        ingredients = validated_data.get("ingredients_amount")
        if ingredients is not None:
            IngredientAmount.objects.filter(recipe=instance).delete()
            self.ingredient_save(instance, ingredients)
        instance.save()
        return instance

    def validate(self, data):
        ingredients_list = []
        ingredients_amount = data.get("ingredients_amount")
        if not ingredients_amount:
            raise serializers.ValidationError("Минимум 1 игридиент необходим")
        for ingredient in ingredients_amount:
            ingredients_list.append(ingredient["ingredient"]["id"])
        if len(ingredients_list) > len(set(ingredients_list)):
            raise serializers.ValidationError(
                {"error": "Ингредиенты должны быть уникальными"}
            )
        tags = data.get("tags")
        if not tags:
            raise serializers.ValidationError(
                {"error": "Должен быть хотябы 1 тег"}
            )
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError(
                {"error": "Тэги должны быть уникальными"}
            )
        cooking_time = data.get("cooking_time")
        if cooking_time <= 0:
            raise serializers.ValidationError(
                {"error": "Время приготовление не может быть меньше 1 минуты"}
            )
        return data

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериализатор избранных рецептов"""

    user = serializers.PrimaryKeyRelatedField(
        queryset=UserModel.objects.all(), write_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(), write_only=True
    )

    class Meta:
        model = Favorite
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=Favorite.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже в избранном",
            )
        ]


class RecipeMiniSerializer(serializers.ModelSerializer):
    """Мини сериалитор для добавления рецепта в избранное"""

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class CartSerializer(serializers.ModelSerializer):
    """Сериализатор корзины покупок"""

    user = serializers.PrimaryKeyRelatedField(
        queryset=UserModel.objects.all(), write_only=True
    )
    recipe = serializers.PrimaryKeyRelatedField(
        queryset=Recipe.objects.all(), write_only=True
    )

    class Meta:
        model = Cart
        fields = ("user", "recipe")
        validators = [
            UniqueTogetherValidator(
                queryset=Cart.objects.all(),
                fields=("user", "recipe"),
                message="Рецепт уже в корзине",
            )
        ]
