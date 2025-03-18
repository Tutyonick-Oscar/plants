from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

urlpatterns = [
    # path('admin/',admin.site.urls),
    re_path("api/", include("agroflex.routes.api_urls")),
    re_path("web/", include("agroflex.routes.web_urls")),
]

# spectacular
urlpatterns += [
    path("api/docs/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
