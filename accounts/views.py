import logging

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView

from .serializers import VerifyCodeSerializer
from django.conf import settings


logger = logging.getLogger(__name__)


@method_decorator(csrf_exempt, name='dispatch')
class VerifyCodeAPIView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=VerifyCodeSerializer,
        responses={
            200: openapi.Response(
                description="Kod muvaffaqiyatli tasdiqlandi.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'success': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'message': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'phone': openapi.Schema(type=openapi.TYPE_STRING, description="Tasdiqlangan telefon raqami"),
                                'verified_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, description="Tasdiqlangan vaqt"),
                                'expires_at': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, nullable=True, description="Kodning amal qilish muddati"),
                            },
                            required=['phone', 'verified_at']
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
                              "Telefon raqami yuborilgan kod orqali avtomatik aniqlanadi."
    )
    def post(self, request, *args, **kwargs): # post metodini sinxron qildik
        try:
            logger.info(f"Verify code request data: {request.data}")

            serializer = VerifyCodeSerializer(data=request.data, context={'request': request})

            if serializer.is_valid():
                validated_data = serializer.validated_data
                phone = validated_data.get('phone') # Serializer ichidan keladi
                code = validated_data.get('code')
                login_code = validated_data.get('login_code')

                logger.info(f"Kod muvaffaqiyatli tasdiqlandi: phone={phone}, code={code}")

                response_data = {
                    'success': True,
                    'message': '✅ Kod muvaffaqiyatli tasdiqlandi!',
                    'data': {
                        'phone': phone,
                        'verified_at': timezone.now().isoformat(),
                        'expires_at': login_code.expires_at.isoformat() if login_code and login_code.expires_at else None
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