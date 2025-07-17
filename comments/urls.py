from rest_framework.routers import DefaultRouter
from .views import CommentViewSet, LikeViewSet, FavoriteViewSet, RatingViewSet

router = DefaultRouter()
router.register('comments', CommentViewSet, basename='comments')
router.register('likes', LikeViewSet, basename='likes')
router.register('favorites', FavoriteViewSet, basename='favorites')
router.register('ratings', RatingViewSet, basename='ratings')

urlpatterns = router.urls
