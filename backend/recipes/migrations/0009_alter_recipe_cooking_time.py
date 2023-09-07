# Generated by Django 3.2.3 on 2023-08-07 17:01

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0008_auto_20230807_2038"),
    ]

    operations = [
        migrations.AlterField(
            model_name="recipe",
            name="cooking_time",
            field=models.PositiveSmallIntegerField(
                default=1,
                validators=[
                    django.core.validators.MinValueValidator(
                        1, "Минимум 1 минута"
                    )
                ],
                verbose_name="Время приготовления",
            ),
        ),
    ]
