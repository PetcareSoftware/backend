from django.urls import path
from . import views

urlpatterns = [
    path('', views.notifications_list, name='notifications-list'),
    path('<int:id>/read/', views.notification_read, name='notification-read'),
    path('read-all/', views.notification_read_all, name='notification-read-all'),
]
