# Generated by Django 4.0.5 on 2022-06-18 19:31
import django.db.models.deletion
from django.db import migrations
from django.db import models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "article",
                    models.CharField(
                        max_length=64,
                        primary_key=True,
                        serialize=False,
                        unique=True,
                        verbose_name="Артикул",
                    ),
                ),
                (
                    "pricing_strategy",
                    models.CharField(
                        choices=[("AVERAGE", "Avarage"), ("EDLP", "EDLP")],
                        max_length=16,
                        verbose_name="Стратегия ценообразования",
                    ),
                ),
                (
                    "parsing_date",
                    models.DateTimeField(null=True, verbose_name="Дата парсинга"),
                ),
                (
                    "available_competitors",
                    models.BooleanField(
                        null=True, verbose_name="В наличии у конкурентов"
                    ),
                ),
                (
                    "new_price",
                    models.IntegerField(null=True, verbose_name="Новая цена"),
                ),
            ],
            options={
                "verbose_name": "Продукт",
                "verbose_name_plural": "Продукты",
                "ordering": ["article"],
            },
        ),
        migrations.CreateModel(
            name="Competitor",
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
                ("article", models.CharField(max_length=64, verbose_name="Артикул")),
                (
                    "product",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="main.product"
                    ),
                ),
            ],
            options={
                "verbose_name": "Конкурент",
                "verbose_name_plural": "Конкуренты",
            },
        ),
    ]
