from rest_framework import serializers

from comments.serializers import CommentSerializer
from .models import Product, ProductImage, CarModel, Brand


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']


class ProductSerializer(serializers.ModelSerializer):
    price_uzs = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    uploaded_images = serializers.ListField(
        child=serializers.ImageField(),
        write_only=True,
        required=False,
        max_length=5
    )

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'car_model',
            'price_usd', 'price_uzs', 'description',
            'youtube_link', 'is_active',
            'images', 'uploaded_images',
            "comments"
        ]
        read_only_fields = ['id', 'price_uzs', 'images', "comments"]

    def get_price_uzs(self, obj):
        return obj.price_uzs

    def create(self, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        product = Product.objects.create(**validated_data)
        for image in uploaded_images:
            ProductImage.objects.create(product=product, image=image)
        return product

    def update(self, instance, validated_data):
        uploaded_images = validated_data.pop('uploaded_images', [])
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        for image in uploaded_images:
            ProductImage.objects.create(product=instance, image=image)
        return instance

    def validate_uploaded_images(self, value):
        if len(value) > 5:
            raise serializers.ValidationError("Maksimal 5 ta rasm yuklashingiz mumkin.")
        return value


class CarModelSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    products = ProductSerializer(many=True, read_only=True)  # car_model.products orqali

    class Meta:
        model = CarModel
        fields = ['id', 'name', 'brand', 'brand_name', 'image', 'products']


class BrandSerializer(serializers.ModelSerializer):
    car_models = CarModelSerializer(many=True, read_only=True)

    class Meta:
        model = Brand
        fields = ['id', 'name', 'image', 'car_models']

