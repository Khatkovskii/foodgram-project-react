from django.db import models


class Ingredient(models.Model):
    name = models.CharField(
        max_length=200,
        blank=False,
        verbose_name='Ингридиент'
    )
    unit = models.CharField(
        max_length=10,
        blank=False,
        verbose_name='Единица измерения'
    )
    
    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингридиент'
        verbose_name_plural = 'Ингридиенты'
    
    def __str__(self) -> str:
        return f'{self.name}, {self.unit}' 