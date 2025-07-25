from rest_framework import serializers
from .models import LoginCode
from django.utils import timezone
from asgiref.sync import sync_to_async, async_to_sync # async_to_sync ni import qildik
import logging

logger = logging.getLogger(__name__)


class VerifyCodeSerializer(serializers.Serializer):
    code = serializers.CharField(
        max_length=5,
        min_length=5,
        help_text="5 xonali tasdiqlash kodi",
        error_messages={
            'required': '❌ Kod majburiy.',
            'max_length': '❌ Kod 5 xonali bo\'lishi kerak.',
            'min_length': '❌ Kod 5 xonali bo\'lishi kerak.',
        }
    )
    phone = serializers.CharField(
        max_length=20,
        help_text="Telefon raqami (API orqali avtomatik aniqlanadi)",
        required=False
    )

    def validate_code(self, value):
        """Kod formatini tekshirish"""
        if not value.isdigit():
            raise serializers.ValidationError("❌ Kod faqat raqamlardan iborat bo'lishi kerak.")
        return value

    def validate(self, data):
        code = data.get("code")
        login_code = async_to_sync(sync_to_async(LoginCode.objects.filter(code=code, is_used=False).first))()

        if not login_code:
            logger.warning(f"Kod topilmadi yoki ishlatilgan: code={code}")
            raise serializers.ValidationError({
                'code': ["❌ Kod noto'g'ri, muddati tugagan yoki ishlatilgan."]
            })

        if login_code.is_expired():
            logger.warning(f"Kod muddati tugagan: code={code}, expires_at={login_code.expires_at}")
            raise serializers.ValidationError({
                'code': ["⌛ Kod muddati tugagan. Yangi kod oling."]
            })

        async_to_sync(sync_to_async(setattr))(login_code, 'is_used', True)
        async_to_sync(sync_to_async(login_code.save))(update_fields=['is_used'])

        data['phone'] = login_code.phone
        data['login_code'] = login_code

        logger.info(f"Kod muvaffaqiyatli tasdiqlandi: phone={login_code.phone}, code={code}")

        return data