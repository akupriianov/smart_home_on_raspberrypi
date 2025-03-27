# v1/lighting_control/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('control-light/', views.control_light, name='control-light'),
]
