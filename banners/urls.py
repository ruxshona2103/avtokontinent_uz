from rest_framework.routers import DefaultRouter
from .views import BannerViewSet

router = DefaultRouter()
router.register('banners', BannerViewSet, basename='banners')

urlpatterns = router.urls
