from django.urls import path
from ..views import CreateTask

urlpatterns = [
    path("<int:field_id>/create/",CreateTask.as_view(),name='create-task-api'),
]