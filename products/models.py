from django.db import models
from setting.models import DollarRate  # dollar kursi uchun

class Brand(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='brands/', null=True, blank=True)

    def str(self):
        return self.name

class CarModel(models.Model):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name="car_models")
    name = models.CharField(max_length=100)
    image = models.ImageField(upload_to='car_models/', null=True, blank=True)

    def str(self):
        return f"{self.brand.name} {self.name}"



    def str(self):
        return f"{self.car_model.name} – {self.name}"

class Product(models.Model):
    name = models.CharField(max_length=255)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    car_model = models.ForeignKey(CarModel, related_name='products', on_delete=models.CASCADE)
    price_usd = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    youtube_link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def str(self):
        return self.name

    @property
    def price_uzs(self):
        rate = DollarRate.get_latest()
        return round(float(self.price_usd) * rate, 2)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_images/', null=True)

    def str(self):
        return f"Image for Product #{self.product.id}"
