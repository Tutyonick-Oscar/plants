from django.apps import AppConfig

from plants.usable import app_path


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = app_path("core")
