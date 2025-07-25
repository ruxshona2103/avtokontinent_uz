from django.db import models

class SiteSettings(models.Model):
    dollar_rate = models.DecimalField(max_digits=10, decimal_places=2)
    card_number = models.CharField(max_length=50)

    def __str__(self):
        return f"Dollar: {self.dollar_rate} | Card: {self.card_number}"

    class Meta:
        verbose_name = 'Site Setting'
        verbose_name_plural = 'Site Settings'



class DollarRate(models.Model):
    rate = models.DecimalField(max_digits=10, decimal_places=2)
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_latest(cls):
        return cls.objects.last().rate if cls.objects.exists() else 12500
