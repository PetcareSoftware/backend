from rest_framework import viewsets
from apps.common.permissions import IsVet
from .models import VaccinationEvent, VaccinationPlan
from .serializers import VaccinationEventSerializer, VaccinationPlanSerializer


class VaccinationPlanViewSet(viewsets.ModelViewSet):
    queryset = VaccinationPlan.objects.prefetch_related('items')
    serializer_class = VaccinationPlanSerializer

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [IsVet()]
        return super().get_permissions()


class VaccinationEventViewSet(viewsets.ModelViewSet):
    queryset = VaccinationEvent.objects.select_related('patient', 'plan_item', 'created_by__user__user')
    serializer_class = VaccinationEventSerializer

    def get_permissions(self):
        if self.action in {'create', 'update', 'partial_update', 'destroy'}:
            return [IsVet()]
        return super().get_permissions()
