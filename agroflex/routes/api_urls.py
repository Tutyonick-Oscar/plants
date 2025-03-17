from django.urls import include, path, re_path

from agroflex.utils import app_path

urlpatterns = [
    path("", include(f"{app_path('plants_species')}.urls")),
    path("", include(f"{app_path('accounts')}.urls.api")),
    path("", include(f"{app_path('field')}.urls.api")),
    path("tasks/", include(f"{app_path('task')}.urls.api")),
    path("", include(f"{app_path('market')}.urls.api")),
    path("", include(f"{app_path('plant')}.urls.api")),
]
