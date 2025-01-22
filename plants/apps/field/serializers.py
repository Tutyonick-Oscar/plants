from plants.apps.user_app.serializers import CustomUserSerializer,DynamicFieldsModelSerializer
from .models import Field


class FieldSerializer(DynamicFieldsModelSerializer):
    created_by = CustomUserSerializer(read_only = True)
    class Meta:
        model = Field
        fields = [
            'id','plant_specie','region','country',
            'start_on','prod_quantity_estimated',
            'measure','period','project_description','grow_speed','created_by',
            'ground_ph',
            'ground_type',
            'organic_materials',
            'long',
            'lat',
            'equipements',
            'agroflex_advices',
        ]

