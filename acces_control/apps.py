#v1/acces_control/apps.py
from django.apps import AppConfig

class AccesControlConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'acces_control'
    verbose_name = 'Kontrola dostępu'
