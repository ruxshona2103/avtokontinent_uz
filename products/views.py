from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Case, When
from rapidfuzz import fuzz
from .models import Product, ProductImage, Brand, CarModel
from .serializers import ProductSerializer, BrandSerializer, CarModelSerializer

class ProductViewSet(ModelViewSet):
    serializer_class = ProductSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['brand', 'car_model', 'car_model__brand']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price_usd']
    ordering = ['id']

    def get_queryset(self):
        base_qs = Product.objects.filter(is_active=False).select_related(
            'brand', 'car_model', 'car_model__brand'
        ).prefetch_related('images')

        query = self.request.query_params.get('search', '').lower().strip()
        if not query:
            return base_qs

        query_words = query.split()
        results = []

        for product in base_qs:
            name = product.name.lower() if product.name else ''
            description = (product.description.lower() if product.description else '')

            combined_text = f"{name} {description}".strip()
            total_score = fuzz.partial_ratio(query, combined_text)

            if len(query_words) > 1:
                word_scores = []
                for word in query_words:
                    word_score = max(
                        fuzz.partial_ratio(word, name),
                        fuzz.partial_ratio(word, description)
                    )
                    word_scores.append(word_score)
                avg_word_score = sum(word_scores) / len(word_words)
                total_score = max(total_score, avg_word_score * 0.8)

            # Pasaytirilgan threshold sinov uchun
            if total_score >= 50:  # 70 o'rniga 50 ni sinab ko'ring
                results.append((product.id, total_score))

        if not results:
            return base_qs.none()

        sorted_ids = [pid for pid, _ in sorted(results, key=lambda x: x[1], reverse=True)]
        preserved_order = Case(*[When(pk=pid, then=pos) for pos, pid in enumerate(sorted_ids)])

        return base_qs.filter(id__in=sorted_ids).order_by(preserved_order)
    def create(self, request, *args, **kwargs):
        uploaded_images = request.FILES.getlist('uploaded_images')
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save()

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