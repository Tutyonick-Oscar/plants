from django.urls import include, path, re_path

from plants.usable import app_path

urlpatterns = [
    path("plants/", include(f"{app_path('plants_species')}.urls")),
    path("", include(f"{app_path('user_app')}.urls.api")),
    path("", include(f"{app_path('field')}.urls.api")),
    path("tasks/", include(f"{app_path('task')}.urls.api")),
    path("market/", include(f"{app_path('market')}.urls.api")),
]
