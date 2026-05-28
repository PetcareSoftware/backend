from rest_framework.routers import DefaultRouter
from .views import BreedViewSet, PetViewSet, SpeciesViewSet

router = DefaultRouter()
router.register('species', SpeciesViewSet, basename='species')
router.register('breeds', BreedViewSet, basename='breeds')
router.register('pets', PetViewSet, basename='pets')
urlpatterns = router.urls
