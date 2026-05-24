from django.urls import path

from owners import views

urlpatterns = [
    # Perfil del propietario autenticado
    path('me/', views.OwnerMeView.as_view(), name='owner-me'),

    # Mascotas del propietario autenticado
    path('me/pets/', views.OwnerMePetsView.as_view(), name='owner-me-pets'),

    # Listado global (solo RECEPTIONIST)
    path('', views.OwnerListView.as_view(), name='owner-list'),

    # Detalle por ID (solo RECEPTIONIST)
    path('<int:pk>/', views.OwnerDetailView.as_view(), name='owner-detail'),
]
