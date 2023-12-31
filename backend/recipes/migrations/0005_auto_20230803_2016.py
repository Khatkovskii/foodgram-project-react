# Generated by Django 3.2.3 on 2023-08-03 16:16

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("recipes", "0004_alter_ingredient_unit"),
    ]

    operations = [
        migrations.CreateModel(
            name="Tag",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        db_index=True, max_length=100, unique=True
                    ),
                ),
                (
                    "color",
                    models.CharField(
                        max_length=10, verbose_name="Цвет HEX код"
                    ),
                ),
                ("slug", models.SlugField(unique=True)),
            ],
            options={
                "verbose_name": "Тег",
                "verbose_name_plural": "Теги",
                "ordering": ("name",),
            },
        ),
        migrations.AddField(
            model_name="recipe",
            name="tags",
            field=models.ManyToManyField(
                related_name="recipes", to="recipes.Tag", verbose_name="Тег"
            ),
        ),
    ]
