from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from django.urls import path,include,re_path
from drf_spectacular.views import SpectacularRedocView,SpectacularAPIView

urlpatterns = [
    #path('admin/',admin.site.urls),
    re_path('api/',include('plants.routes.api_urls')),
    re_path('',include('plants.routes.web_urls')),
]

# specular
urlpatterns += [
    path("api/docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)