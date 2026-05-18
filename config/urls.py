"""
URL configuration for petcare project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
<<<<<<< HEAD
=======

from django.contrib import admin
>>>>>>> 774e5504c4d5fe62b1ea4c0344a657d6f81241b0
from django.urls import path
from . import views

urlpatterns = [
<<<<<<< HEAD
    path('login/veterinario/', views.login_veterinario, name='login_veterinario'),
]
=======
    path("admin/", admin.site.urls),
]
>>>>>>> 774e5504c4d5fe62b1ea4c0344a657d6f81241b0
