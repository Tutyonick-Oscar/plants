from plants.apps.core.serializers import DynamicFieldsModelSerializer
from plants.apps.market.models.market import Product
from plants.apps.field.serializers import FieldSerializer
from plants.apps.core.middlewares import local
from django.core.exceptions import ValidationError

class ProductSerializer(DynamicFieldsModelSerializer):
    product_field = FieldSerializer(
        read_only = True,
        fields=('id','plant_specie','region','country',)
    )
    class Meta:
        model = Product
        fields = [
            'id',
            'product_name',
            'product_type',
            'product_country',
            'product_region',
            'product_quantity',
            'product_measurement_unit',
            'product_price',
            'product_field'
        ]

    