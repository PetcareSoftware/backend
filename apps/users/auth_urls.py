from django.urls import path

from .views import AuthProxyView, ChangePasswordView, MeView

urlpatterns = [
    path('register/', AuthProxyView.as_view(action='register'), name='auth-register'),
    path('login/', AuthProxyView.as_view(action='login'), name='auth-login'),
    path('refresh/', AuthProxyView.as_view(action='refresh'), name='auth-refresh'),
    path('logout/', AuthProxyView.as_view(action='logout'), name='auth-logout'),
    path('me/', MeView.as_view(), name='auth-me'),
    path('password/', ChangePasswordView.as_view(), name='auth-password'),
    path('change-password/', ChangePasswordView.as_view(), name='auth-change-password'),
]
