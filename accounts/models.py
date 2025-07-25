from django.db import models
from django.utils import timezone
from datetime import timedelta


class LoginCode(models.Model):
    phone = models.CharField(max_length=20, db_index=True, verbose_name="Telefon raqami")
    code = models.CharField(max_length=5, verbose_name="Tasdiqlash kodi")
    telegram_id = models.BigIntegerField(null=True, blank=True, db_index=True, verbose_name="Telegram ID")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Yaratilgan vaqt")
    expires_at = models.DateTimeField(verbose_name="Tugash vaqti")
    is_used = models.BooleanField(default=False, verbose_name="Ishlatilganmi")

    class Meta:
        verbose_name = "Login Kod"
        verbose_name_plural = "Login Kodlar"
        indexes = [
            models.Index(fields=['phone', 'expires_at']),
            models.Index(fields=['telegram_id']),
            models.Index(fields=['code', 'expires_at']),
        ]

    def __str__(self):
        return f"{self.phone} - {self.code}"

    def is_expired(self):
        return self.expires_at < timezone.now()
    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(days=3)
        super().save(*args, **kwargs)