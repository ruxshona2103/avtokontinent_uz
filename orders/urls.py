from rest_framework.routers import DefaultRouter
from .views import CartItemViewSet, OrderViewSet

router = DefaultRouter()
router.register('cart', CartItemViewSet, basename='cart')
router.register('orders', OrderViewSet, basename='orders')

urlpatterns = router.urls
