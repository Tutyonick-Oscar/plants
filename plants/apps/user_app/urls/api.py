from django.urls import include, path
from rest_framework import routers
from rest_framework.authtoken import views

from plants.apps.core.views import init_request_offset

from ..views import UsersViewSet

app_name = "user_app"
router = routers.DefaultRouter()
router.register(r"accounts", UsersViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
    path("login/", views.obtain_auth_token, name="api-login"),
    path("init-offset/", init_request_offset, name="init-offset-request"),
]
