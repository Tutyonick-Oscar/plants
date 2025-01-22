from django.apps import AppConfig
from plants.usable import app_path


class MarketConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = app_path('market')