from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers


UserModel = get_user_model()


class UserCreateSerializer(UserCreateSerializer):
    """Создание нового пользователя"""

    class Meta:
        model = UserModel
        fields = (
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "password",
        )

    def validate_password(self, value):
        validate_password(value)
        return value

    def validate(self, data):
        """Проверка вводимых данных при регистрации"""

        username = data.get("username")
        email = data.get("email")
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        if UserModel.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                f"email:{email} уже зарегестрирован"
            )
        if UserModel.objects.filter(username__iexact=username).exists():
            raise serializers.ValidationError(
                f"username:{username} уже зарегистрирован"
            )
        if username.lower() == "me":
            raise serializers.ValidationError(
                f"username:{username} запрещен к использованию!"
            )
        if not first_name:
            raise serializers.ValidationError({"Это поле обязательно"})
        if not last_name:
            raise serializers.ValidationError({"Это поле обязательно"})
        return data


class UserReadSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserModel
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
        )

    def get_is_subscribed(self, author):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user.follower.filter(author=author).exists()
        return False


class SetPasswordSerializer(serializers.Serializer):
    """Сериализатор изменения пароля"""

    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        validate_password(value)
        return value

    def update(self, instance, validated_data):
        current_password = validated_data.get("current_password")
        new_password = validated_data.get("new_password")
        if not instance.check_password(current_password):
            raise serializers.ValidationError(
                {"current_password": "Пароль неверный"}
            )
        if current_password == new_password:
            raise serializers.ValidationError(
                {
                    "new_password": "Новый пароль должен отличаться"
                    "от предидущего"
                }
            )
        instance.set_password(new_password)
        instance.save()
        return validated_data


class FollowAuthorSerializer(serializers.ModelSerializer):
    """Сериализатор подписки/отписки на автора"""
    recipes = serializers.SerializerMethodField()
    author = serializers.ReadOnlyField()
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count", read_only=True
    )

    class Meta:
        model = UserModel
        fields = (
            "author",
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def validate(self, data):
        user = self.context["request"].user
        author = self.context["author"]
        if user == author:
            raise serializers.ValidationError(
                {"Невозможно подписаться на самого себя."}
            )
        if user.follower.filter(author=author).exists():
            raise serializers.ValidationError({"Вы уже подписаны на автора"})
        return data

    def get_is_subscribed(self, author):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and user.follower.filter(author=author).exists()
        )

    def get_recipes(self, obj):
        from api.serializers import RecipeMiniSerializer
        recipes = obj.recipes.all()
        serializer = RecipeMiniSerializer(recipes, many=True, read_only=True)
        return serializer.data


class FollowListSerializer(serializers.ModelSerializer):
    """Сериализатор списка подписок на авторов"""
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.IntegerField(
        source="recipes.count", read_only=True
    )

    class Meta:
        model = UserModel
        fields = (
            "id",
            "email",
            "username",
            "first_name",
            "last_name",
            "is_subscribed",
            "recipes",
            "recipes_count",
        )

    def get_is_subscribed(self, author):
        user = self.context["request"].user
        return (
            user.is_authenticated
            and user.follower.filter(author=author).exists()
        )

    def get_recipes(self, obj):
        """Вывод списка рецептов"""
        from api.serializers import RecipeSerializer
        recipes = obj.recipes.all()
        serializer = RecipeSerializer(recipes, many=True, read_only=True)
        return serializer.data
