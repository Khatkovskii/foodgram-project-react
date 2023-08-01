from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

from users.models import User
from api.params import MIN_AMOUNT, MAX_AMOUNT


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        db_index=False,
        verbose_name='Ингридиент'
    )
    unit = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Единица измерения'
    )
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
    
    def __str__(self) -> str:
        return f'{self.name}, {self.unit}'


class Recipe(models.Model):
    name = models.CharField(
        max_length=255,
        db_index=True,
        verbose_name='Рецепт'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='recipes',
        verbose_name='Список ингридиентов',
    )
    image = models.ImageField(
        blank=True,
        upload_to='recipes/images',
        verbose_name='Фото'
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )
    
    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


    def __str__(self) -> str:
        return f'{self.name} автор {self.author.username}'

class IngredientAmount(models.Model):
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Ингридиент'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient_amount',
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        default=MIN_AMOUNT,
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
        ordering = ('-id',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
    
    def __str__(self) -> str:
        return f'{self.ingredient}: {self.amount}'