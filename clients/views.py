from rest_framework import generics, permissions
from rest_framework.response import Response
from .models import CustomUser
from .serializers import UserSerializer
from rest_framework import viewsets
from rest_framework.decorators import action

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class UserViewSet(viewsets.ModelViewSet):
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=False, methods=['get'])
    def profile(self, request):
        """Foydalanuvchi o'z profilini oladi"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    def get_queryset(self):
        # Faqat o'z ma'lumotlarini ko'rishi mumkin
        return CustomUser.objects.filter(id=self.request.user.id)
