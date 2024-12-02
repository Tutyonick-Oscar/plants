from django.contrib import admin
from django.urls import path,include,re_path

urlpatterns = [
    #path('admin/',admin.site.urls),
    re_path('api/',include('plants.routes.api_urls')),
]
