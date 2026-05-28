from rest_framework.routers import DefaultRouter
from .views import WaitingListViewSet

router = DefaultRouter()
router.register('waiting-list', WaitingListViewSet, basename='waiting-list')
urlpatterns = router.urls
