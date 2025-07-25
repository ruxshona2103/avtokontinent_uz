from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import Product, ProductImage, Brand, CarModel
from .serializers import ProductSerializer, BrandSerializer, CarModelSerializer
from rest_framework.response import Response
from rest_framework import status



class ProductViewSet(ModelViewSet):
    queryset = Product.objects.filter(is_active=True).select_related(
        'brand', 'car_model', 'car_model__brand'
    ).prefetch_related('images')
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['brand', 'car_model', 'car_model__brand']
    search_fields = ['name', 'description', 'car_model__name', 'car_model__brand__name']
    ordering_fields = ['name', 'price_usd']
    ordering = ['id']

    def create(self, request, *args, **kwargs):
        # uploaded_images Swagger'da ko‘rinmasin, lekin frontenddan kelganini qabul qil
        uploaded_images = request.FILES.getlist('uploaded_images')

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

        # Rasm bo‘lsa, alohida saqlaymiz
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class BrandViewSet(ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [SearchFilter]
    search_fields = ['name']


class CarModelViewSet(ModelViewSet):
    queryset = CarModel.objects.select_related('brand').all()
    serializer_class = CarModelSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_fields = ['brand']
    search_fields = ['name', 'brand__name']
