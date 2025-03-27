#v1/v1/urls.py
from django.contrib import admin
from django.urls import path, include
from . import views
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('lighting/', include('lighting_control.urls')),
    path('shutters/', include('shutter_control.urls')),
    path('acces/', include('acces_control.urls')),
    path('alarm/', include('alarm_system.urls')),
    # Ścieżki logowania/wylogowania
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]
