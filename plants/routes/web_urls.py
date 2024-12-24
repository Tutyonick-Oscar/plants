from django.urls import path,re_path,include
from plants.usable import app_path


urlpatterns = [
    path("tasks/",include(f"{app_path('task')}.urls.web")),
]