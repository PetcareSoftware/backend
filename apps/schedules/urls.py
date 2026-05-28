from rest_framework.routers import DefaultRouter
from .views import ScheduleViewSet, VetViewSet

router = DefaultRouter()
router.register('vets', VetViewSet, basename='vets')
router.register('schedules', ScheduleViewSet, basename='schedules')
urlpatterns = router.urls
