from rest_framework import routers

from gbb.api.views import ProductViewSet

router = routers.SimpleRouter()
router.register(r"products", ProductViewSet)
