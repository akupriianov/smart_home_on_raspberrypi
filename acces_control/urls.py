# access_control/urls.py
from django.urls import path
from .views import get_latest_card, logs_json
from .views import CardListView, CardCreateView, CardDeleteView, AccesLogListView

#app_name = 'acces'

urlpatterns = [
    path('cards/', CardListView.as_view(), name='card-list'),
    path('cards/add/', CardCreateView.as_view(), name='card-add'),
    path('cards/delete/<int:pk>/', CardDeleteView.as_view(), name='card-delete'),
    path('get-latest-card/', get_latest_card, name='get-latest-card'),
    path('logs/', AccesLogListView.as_view(), name='access-log-list'),
    path('logs.json', logs_json, name='logs-json'),
]
