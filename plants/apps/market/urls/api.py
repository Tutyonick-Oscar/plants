from django.urls import path,include
from rest_framework.routers import DefaultRouter
from plants.apps.market.views.product import ProductViewSet,FieldProductView

router = DefaultRouter()
router.register(r'products',ProductViewSet,basename='products')
app_name = 'market'


urlpatterns = [
    path("",include(router.urls)),
    path("<int:field_pk>/products/",FieldProductView.as_view(),name='field_product'),
]