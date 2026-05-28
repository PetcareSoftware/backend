from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Importamos las vistas correctamente desde tu app users
from apps.users import views
from apps.users.views import LogDashboardView
urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('apps.users.urls')),
    path('login/veterinarian/', views.login_veterinarian, name='login_veterinarian'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('logs-dashboard/', LogDashboardView.as_view(), name='logs_dashboard'),
]