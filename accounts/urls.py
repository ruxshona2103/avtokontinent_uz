from django.urls import path
from .views import VerifyCodeAPIView  # Faqat VerifyCodeAPIView import qilindi

urlpatterns = [
    path('verify-code/', VerifyCodeAPIView.as_view(), name='verify-code'),

]