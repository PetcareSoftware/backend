from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.owner_me, name='owner-me'),
    path('me/pets/', views.owner_me_pets, name='owner-me-pets'),
]
