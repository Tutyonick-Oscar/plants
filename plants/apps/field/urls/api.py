from django.urls import path
from ..views import CreateField

urlpatterns =[
    path("create/",CreateField.as_view(),name='create-field-api')
]