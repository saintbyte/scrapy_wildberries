from django.contrib import admin

from gbb.main.models import Competitor
from gbb.main.models import Product


class CompetitorInline(admin.StackedInline):
    model = Competitor
    extra = 0


class ProductAdmin(admin.ModelAdmin):
    list_display = [
        "article",
        "pricing_strategy",
        "parsing_date",
        "available_competitors",
        "new_price",
    ]
    search_fields = [
        "article",
    ]
    inlines = (CompetitorInline,)


admin.site.register(Product, ProductAdmin)
