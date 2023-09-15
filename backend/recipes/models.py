from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth import get_user_model

from api.params import MAX_AMOUNT, MIN_AMOUNT


UserModel = get_user_model()


class Ingredient(models.Model):
    """Модель ингридиента"""

    name = models.CharField(
        max_length=200, blank=False, db_index=True, verbose_name="Ингридиент"
    )
    measurement_unit = models.CharField(
        max_length=200, blank=False, verbose_name="Единица измерения"
    )

    class Meta:
        ordering = ("name",)
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "measurement_unit"],
                name="unique_ingredient"
            )
        ]

    def __str__(self) -> str:
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    """Модель тэгов"""

    name = models.CharField(max_length=200, db_index=True, unique=True)
    color = models.CharField(
        max_length=7, verbose_name="Цвет HEX код", unique=True
    )
    slug = models.SlugField(max_length=200, unique=True, db_index=True)

    class Meta:
        ordering = ("name",)
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        constraints = [
            models.UniqueConstraint(
                fields=["name", "color"],
                name="unique_tags",
            )
        ]

    def __str__(self):
        return self.name


class NewQuerySet(models.QuerySet):
    """Новый QuerySet для работы с избранным и списком покупок"""

    def add_annotations(self, user_id):
        return self.annotate(
            is_favorited=models.Exists(
                Favorite.objects.filter(
                    recipe__pk=models.OuterRef("pk"), user_id=user_id
                )
            ),
            is_in_shopping_cart=models.Exists(
                Cart.objects.filter(
                    recipe__pk=models.OuterRef("pk"), user_id=user_id
                )
            ),
        )


class Recipe(models.Model):
    """Модель рецептов"""

    name = models.CharField(
        max_length=200, db_index=True, verbose_name="Рецепт"
    )
    author = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор",
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name="recipes",
        verbose_name="Список ингридиентов",
    )
    image = models.ImageField(
        blank=False, upload_to="recipes/images", verbose_name="Фото"
    )
    text = models.TextField(verbose_name="Описание")
    pub_date = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата публикации"
    )
    tags = models.ManyToManyField(
        Tag, related_name="recipes", verbose_name="Тег"
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name="Время приготовления",
        validators=[
            MinValueValidator(MIN_AMOUNT, f"Минимум {MIN_AMOUNT} минута")
        ],
        default=MIN_AMOUNT,
    )
    objects = NewQuerySet.as_manager()

    class Meta:
        ordering = ("-pub_date",)
        verbose_name = "Рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self) -> str:
        return f"{self.name} автор {self.author.username}"


class IngredientAmount(models.Model):
    """Модель количества ингридиетов"""

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name="ingredients_amount",
        verbose_name="Ингридиент",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="ingredients_amount",
        verbose_name="Рецепт",
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name="Количество",
        default=MIN_AMOUNT,
        validators=[
            MinValueValidator(
                MIN_AMOUNT,
                "Минимальное количество ингридиентов: " f"{MIN_AMOUNT}",
            ),
            MaxValueValidator(
                MAX_AMOUNT,
                "Максимальное количество ингридиентов: " f"{MAX_AMOUNT}",
            ),
        ],
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Ингридиент"
        verbose_name_plural = "Ингридиенты"

    def __str__(self) -> str:
        return f"{self.ingredient}: {self.amount}"


class Favorite(models.Model):
    """Модель избранных рецептов"""

    recipe = models.ForeignKey(
        Recipe,
        verbose_name="Рецепт",
        related_name="favorite",
        on_delete=models.CASCADE,
    )
    user = models.ForeignKey(
        UserModel,
        verbose_name="Пользователь",
        related_name="favorite",
        on_delete=models.CASCADE,
    )
    add_date = models.DateField(
        verbose_name="Дата добавления",
        editable=False,
        auto_now_add=True,
    )

    class Meta:
        ordering = ("user",)
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_favorite",
            )
        ]


class Cart(models.Model):
    """Модель корзины покупок"""

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт",
        related_name="cart",
    )
    user = models.ForeignKey(
        UserModel,
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        related_name="cart",
    )
    add_date = models.DateField(
        verbose_name="Дата добавления",
        editable=False,
        auto_now_add=True,
    )

    class Meta:
        ordering = ("-id",)
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"
        constraints = [
            models.UniqueConstraint(
                fields=["recipe", "user"],
                name="unique_cart",
            )
        ]
    def __str__(self) -> str:
        return f"Корзина для {self.user.username}: {self.recipe.name}"
