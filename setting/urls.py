from rest_framework.routers import DefaultRouter
from .views import SiteSettingsViewSet

router = DefaultRouter()
router.register(r'setting', SiteSettingsViewSet, basename='setting')

urlpatterns = router.urls
