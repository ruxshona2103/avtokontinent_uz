from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    ProductViewSet,
    BrandViewSet,
    CarModelViewSet,
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'brands', BrandViewSet, basename='brand')
router.register(r'car-models', CarModelViewSet, basename='carmodel')

urlpatterns = [
    path('', include(router.urls)),
]
