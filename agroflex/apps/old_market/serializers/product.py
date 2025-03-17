from agroflex.apps.core.serializers import DynamicFieldsModelSerializer
from agroflex.apps.field.serializers import FieldSerializer
from agroflex.apps.old_market.models.market import Product
from agroflex.apps.user_app.serializers import CustomUserSerializer


class ProductSerializer(DynamicFieldsModelSerializer):
    product_field = FieldSerializer(
        read_only=True,
        fields=(
            "id",
            "plant_specie",
            "region",
            "country",
        ),
    )
    created_by = CustomUserSerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            "id",
            "product_name",
            "product_type",
            "product_country",
            "product_region",
            "product_quantity",
            "product_measurement_unit",
            "product_price",
            "product_field",
            "created_by",
        ]
