from plants.apps.user_app.serializers import CustomUserSerializer,DynamicFieldsModelSerializer
from .models import Field

class FieldSerializer(DynamicFieldsModelSerializer):
    created_by = CustomUserSerializer(read_only = True)
    class Meta:
        model = Field
        fields = ['id','plant_specie','region','start_on','mesure','accuracy','created_by']