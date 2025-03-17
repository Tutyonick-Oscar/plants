from django.urls import include, path
from rest_framework.routers import DefaultRouter

from agroflex.apps.old_market.views.product import FieldProductView, ProductViewSet

router = DefaultRouter()
router.register(r"products", ProductViewSet, basename="products")
app_name = "market"


urlpatterns = [
    path("", include(router.urls)),
    path("<int:field_pk>/products/", FieldProductView.as_view(), name="field_product"),
]
