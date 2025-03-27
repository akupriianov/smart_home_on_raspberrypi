# v1/alarm_system/urls.py
from django.urls import path
from .views import AlarmEventListView, toggle_alarm_view

urlpatterns = [
    path('events/', AlarmEventListView.as_view(), name='alarm-events-list'),
    path('toggle/', toggle_alarm_view, name='alarm-toggle'),
]
