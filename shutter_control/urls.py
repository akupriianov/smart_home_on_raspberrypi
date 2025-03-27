# v1/shutter_control/urls.py
from django.urls import path
from .views import shutter_control_view

urlpatterns = [
    path('panel/', shutter_control_view, name='shutter-control'),
]
