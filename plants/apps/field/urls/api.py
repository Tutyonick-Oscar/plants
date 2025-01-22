from django.urls import path,include
from ..views import FieldViewSet,FieldMonitoringView
from rest_framework import routers

app_name = 'field'
router = routers.DefaultRouter()
router.register(r'fields',FieldViewSet,basename='fields')

urlpatterns=[
    path("",include(router.urls)),
    path("field/<int:field_id>/monitor/",FieldMonitoringView.as_view(),name='field-monitor-api'),
]