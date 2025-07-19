# orders/views.py
from rest_framework import viewsets, permissions
from .models import Order
from .serializers import OrderSerializer, OrderCreateSerializer


class OrderViewSet(viewsets.ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['create']:
            return OrderCreateSerializer
        return OrderSerializer

    def get_queryset(self):
        # Swagger schema generatsiya uchun tekshirish
        if getattr(self, 'swagger_fake_view', False):
            return self.queryset.none()

        # Foydalanuvchi autentifikatsiya qilinganmi tekshirish
        if not self.request.user.is_authenticated:
            return self.queryset.none()

        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)