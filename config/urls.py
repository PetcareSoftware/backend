from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.permissions import AllowAny

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/schema/', SpectacularAPIView.as_view(permission_classes=[AllowAny]), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema', permission_classes=[AllowAny]), name='swagger-ui'),
    path('api/v1/auth/', include('apps.users.auth_urls')),
    path('api/v1/', include('apps.owners.urls')),
    path('api/v1/', include('apps.pets.urls')),
    path('api/v1/', include('apps.schedules.urls')),
    path('api/v1/', include('apps.appointments.urls')),
    path('api/v1/', include('apps.appointments.waiting_urls')),
    path('api/v1/', include('apps.notifications.urls')),
    path('api/v1/', include('apps.medical_records.urls')),
    path('api/v1/', include('apps.vaccinations.urls')),
]
