from django.urls import path 
from ..resources.views.ussd import generate_user_ident

urlpatterns = [
    path("user-ident/",generate_user_ident,name='generate-user-ident'),
]