from django.db import models
from django.utils.translation import gettext as _


class Product(models.Model):
    class PricingStrategy(models.TextChoices):
        AVERAGE = "AVERAGE", _("Avarage")
        EDLP = "EDLP", _("EDLP")

    article = models.CharField(
        max_length=64, unique=True, primary_key=True, verbose_name=_("Артикул")
    )
    pricing_strategy = models.CharField(
        max_length=16,
        verbose_name=_("Стратегия ценообразования"),
        choices=PricingStrategy.choices,
    )
    parsing_date = models.DateTimeField(null=True, verbose_name=_("Дата парсинга"))
    available_competitors = models.BooleanField(
        null=True, verbose_name=_("В наличии у конкурентов")
    )
    new_price = models.PositiveBigIntegerField(
        null=True,
        verbose_name=_("Новая цена"),
        help_text=_("Валюта Российский рубль, в копейках"),
    )

    @property
    def as_string(self):
        return self.article

    def __str__(self):
        return self.as_string

    class Meta:
        ordering = [
            "article",
        ]
        verbose_name = _("Продукт")
        verbose_name_plural = _("Продукты")


class Competitor(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    article = models.CharField(max_length=64, verbose_name=_("Артикул"))

    @property
    def as_string(self):
        return self.article

    def __str__(self):
        return self.as_string

    class Meta:
        verbose_name = _("Конкурент")
        verbose_name_plural = _("Конкуренты")
