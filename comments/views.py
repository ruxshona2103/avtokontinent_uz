from rest_framework import viewsets, permissions
from .models import Comment, Like, Favorite, Rating
from .serializers import CommentSerializer, LikeSerializer, FavoriteSerializer, RatingSerializer


class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all().order_by('-created_at')
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class LikeViewSet(viewsets.ModelViewSet):
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Favorite.objects.none()

        if not self.request.user.is_authenticated:
            return Favorite.objects.none()

        return Favorite.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RatingViewSet(viewsets.ModelViewSet):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # Swagger schema generatsiya uchun tekshirish
        if getattr(self, 'swagger_fake_view', False):
            return Rating.objects.none()

        # Foydalanuvchi autentifikatsiya qilinganmi tekshirish
        if not self.request.user.is_authenticated:
            return Rating.objects.none()

        return Rating.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
