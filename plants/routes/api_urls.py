from django.urls import path,re_path,include
from plants.usable import app_path
from plants.apps.core.views import InitRequestOffset

urlpatterns = [
    path("plants/",include(f"{app_path('plants_species')}.urls")),
    path("",include(f"{app_path('user_app')}.urls.api")),
    path("",include(f"{app_path('field')}.urls.api")),
    path("tasks/",include(f"{app_path('task')}.urls.api")),
    path("init-offset",InitRequestOffset.as_view(),name="init-offset-request")
]