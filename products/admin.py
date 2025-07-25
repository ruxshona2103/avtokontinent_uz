from django.contrib import admin
from .models import Product,  Brand, ProductImage

admin.site.register(Product)
admin.site.register(Brand)
admin.site.register(ProductImage)
