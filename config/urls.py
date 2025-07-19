from django.contrib import admin
from django.urls import path, re_path, include
from django.conf import settings
from django.conf.urls.static import static

from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from drf_yasg.generators import OpenAPISchemaGenerator
from rest_framework import permissions


# Swagger JWT uchun kerakli security schema
class JWTSchemaGenerator(OpenAPISchemaGenerator):
    def get_security_definitions(self):
        security_definitions = super().get_security_definitions()
        security_definitions['Bearer'] = {
            'type': 'apiKey',
            'name': 'Authorization',
            'in': 'header'
        }
        return security_definitions


schema_view = get_schema_view(
    openapi.Info(
        title="Avtokontinent Uz",  # O'zgartirishingiz mumkin
        default_version='v1',
        description="QuickCare site API documentation",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="your_email@example.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
    generator_class=JWTSchemaGenerator,
)

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/', include('clients.urls')),            # clients
    path('api/', include('products.urls')),           # products
    path('api/', include('banners.urls')),            # banners
    path('api/', include('orders.urls')),             # orders
    path('api/', include('comments.urls')),           # comments, likes, favorites, ratings
    path('api/', include('setting.urls')),            # site settings

    # Swagger
    re_path(r'^swagger(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name='schema-json'),
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),
]

# Media file'lar uchun
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
