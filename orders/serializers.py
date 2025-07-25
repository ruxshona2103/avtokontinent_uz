from rest_framework import serializers
from .models import CartItem, Product, OrderItem, Order


class CartItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'created_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'product_name', 'quantity', 'price']


class OrderCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField(write_only=True)

    class Meta:
        model = Order
        fields = ['id', 'full_name', 'address', 'phone_number', 'product_id', 'quantity']

    def create(self, validated_data):
        request = self.context.get('request')
        product_id = validated_data.pop('product_id')
        quantity = validated_data.pop('quantity')

        product = Product.objects.get(id=product_id)

        user = request.user if request and request.user.is_authenticated else None

        order = Order.objects.create(
            user=user,
            full_name=validated_data['full_name'],
            address=validated_data['address'],
            phone_number=validated_data['phone_number']
        )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price_usd
        )

        return order


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(source='orderitem_set', many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'full_name', 'address', 'phone_number', 'created_at', 'status', 'is_paid', 'items']
