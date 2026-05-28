from rest_framework.routers import DefaultRouter
from .views import ConsultationViewSet, MedicalRecordViewSet

router = DefaultRouter()
router.register('consultations', ConsultationViewSet, basename='consultations')
router.register('medical-records', MedicalRecordViewSet, basename='medical-records')
urlpatterns = router.urls
