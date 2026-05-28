# Las rutas formales de vacunación son anidadas por mascota en apps.pets.urls:
# /api/v1/pets/{id}/vaccination-plan/
# /api/v1/pets/{id}/vaccination-plan/schedule/
# /api/v1/pets/{id}/vaccination-events/
# No se exponen ModelViewSet globales para evitar escrituras sin patient_id.
urlpatterns = []
