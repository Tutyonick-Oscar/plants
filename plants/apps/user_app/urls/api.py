from django.urls import path
from ..views import CreateUser
from rest_framework.authtoken import views


urlpatterns =[
    path('create/',CreateUser.as_view(),name="create-user"),
    path('login/',views.obtain_auth_token,name='api-login')
]