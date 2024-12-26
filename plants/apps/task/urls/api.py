from django.urls import path
from ..views import CreateTask
from ..resources.views.ussd import GenerateUserIdent

urlpatterns = [
    path("<int:field_id>/create/",CreateTask.as_view(),name='create-task-api'),
    path("user-ident/",GenerateUserIdent.as_view(),name='generate-user-ident'),
]