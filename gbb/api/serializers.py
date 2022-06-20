from rest_framework import serializers

from gbb.main.models import Product


class ProductSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = [
            "article",
            "pricing_strategy",
            "parsing_date",
            "available_competitors",
            "new_price",
        ]
