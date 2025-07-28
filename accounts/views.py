# accounts/views.py (Yangi va to'liq JWT qaytaradigan versiya)

import logging

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model  # User modelini olish uchun
from rest_framework_simplejwt.tokens import RefreshToken  # JWT yaratish uchun

from .serializers import VerifyCodeSerializer
from django.conf import settings
from .models import LoginCode  # LoginCode modelini ham import qiling

logger = logging.getLogger(__name__)

User = get_user_model()  # Foydalanuvchi modelini olish


@method_decorator(csrf_exempt, name='dispatch')
class VerifyCodeAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=VerifyCodeSerializer,
        responses={
            200: openapi.Response(
                description="Kod muvaffaqiyatli tasdiqlandi va tokenlar qaytarildi.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'phone': openapi.Schema(type=openapi.TYPE_STRING,
                                                        description="Tasdiqlangan telefon raqami"),
                                'verified_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                                                              description="Tasdiqlangan vaqt"),
                                'expires_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME,
                                                             nullable=True, description="Kodning amal qilish muddati"),
                                'access': openapi.Schema(type=openapi.TYPE_STRING, description="JWT Access Token"),
                                # Yangi
                                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description="JWT Refresh Token"),
                                # Yangi
                            },
                            required=['phone', 'verified_at', 'access', 'refresh']  # Yangi
                        ),
                    },
                    required=['success', 'message', 'data']
                )
            ),
            400: openapi.Response(
                description="Kod tasdiqlashda xatolik.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'errors': openapi.Schema(type=openapi.TYPE_OBJECT, description="Validatsiya xatolari"),
                    },
                    required=['success', 'message', 'errors']
                )
            ),
            500: openapi.Response(
                description="Server xatoligi.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'error': openapi.Schema(type=openapi.TYPE_STRING, description="Xatolik xabari"),
                    },
                    required=['success', 'message', 'error']
                )
            ),
        },
        operation_description="Foydalanuvchi tomonidan yuborilgan 5 xonali kodni tasdiqlaydi. "
                              "Bu API asosan web-interfeysdan foydalanuvchi kiritgan kodni tekshirish uchun ishlatiladi. "
                              "Telefon raqami yuborilgan kod orqali avtomatik aniqlanadi. "
                              "Muvaffaqiyatli tasdiqlansa, JWT access va refresh tokenlari qaytariladi."
    )
    def post(self, request, *args, **kwargs):
        try:
            logger.info(f"Verify code request data: {request.data}")

            serializer = VerifyCodeSerializer(data=request.data, context={'request': request})

            if serializer.is_valid():
                validated_data = serializer.validated_data
                phone = validated_data.get('phone')
                code = validated_data.get('code')
                login_code_instance = validated_data.get('login_code')  # Serializer dan LoginCode obyektini olamiz

                logger.info(f"Kod muvaffaqiyatli tasdiqlandi: phone={phone}, code={code}")

                # Foydalanuvchini topish yoki yaratish
                try:
                    user, created = User.objects.get_or_create(
                        phone_number=phone,
                        defaults={'username': phone}  # Agar username fieldi phone bo'lmasa, moslang
                    )
                except Exception as e:
                    logger.error(f"Foydalanuvchi yaratish/topishda xatolik: {e}")
                    return Response({
                        'success': False,
                        'message': '❌ Foydalanuvchini qayta ishlashda xatolik yuz berdi.',
                        'error': str(e) if settings.DEBUG else 'Internal server error'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                # JWT tokenlarini yaratish
                try:
                    refresh = RefreshToken.for_user(user)
                    access_token = str(refresh.access_token)
                    refresh_token = str(refresh)
                except Exception as e:
                    logger.error(f"JWT yaratishda xatolik: {e}")
                    return Response({
                        'success': False,
                        'message': '❌ Token yaratishda xatolik yuz berdi.',
                        'error': str(e) if settings.DEBUG else 'Internal server error'
                    }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

                response_data = {
                    'success': True,
                    'message': '✅ Kod muvaffaqiyatli tasdiqlandi va siz kirishingiz mumkin!',
                    'data': {
                        'phone': phone,
                        'verified_at': timezone.now().isoformat(),
                        'expires_at': login_code_instance.expires_at.isoformat() if login_code_instance and login_code_instance.expires_at else None,
                        'access': access_token,  # JWT Access Token
                        'refresh': refresh_token,  # JWT Refresh Token
                    }
                }
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                logger.warning(f"Validatsiya xatoliklari: {serializer.errors}")
                return Response({
                    'success': False,
                    'message': '❌ Kod tasdiqlashda xatolik.',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.exception("VerifyCodeAPIView'da kutilmagan xatolik:")
            return Response({
                'success': False,
                'message': '❌ Server xatoligi yuz berdi.',
                'error': str(e) if settings.DEBUG else 'Internal server error'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
