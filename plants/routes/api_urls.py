from django.urls import path,re_path,include
from plants.usable import app_path

urlpatterns = [
    path('plants/',include(f'{app_path('plants_species')}.urls')),
    path('accounts/',include(f'{app_path('user_app')}.urls.api')),
    path('fields/',include(f'{app_path('field')}.urls.api'))
]