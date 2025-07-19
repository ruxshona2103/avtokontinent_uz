from rest_framework.viewsets import ModelViewSet
from .models import Banner
from .serializers import BannerSerializer
from rest_framework.permissions import IsAdminUser, AllowAny

class BannerViewSet(ModelViewSet):
    queryset = Banner.objects.all()
    serializer_class = BannerSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAdminUser()]
