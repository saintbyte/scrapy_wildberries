from rest_framework import viewsets

from gbb.api.serializers import ProductSimpleSerializer
from gbb.main.models import Product


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSimpleSerializer
