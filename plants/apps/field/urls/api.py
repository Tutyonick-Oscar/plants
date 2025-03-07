from django.urls import include, path
from rest_framework import routers

from ..views import FieldMonitoringView, FieldViewSet

app_name = "field"
router = routers.DefaultRouter()
router.register(r"fields", FieldViewSet, basename="fields")

urlpatterns = [
    path("", include(router.urls)),
    path(
        "field/<int:field_id>/monitor/",
        FieldMonitoringView.as_view(),
        name="field-monitor-api",
    ),
]
