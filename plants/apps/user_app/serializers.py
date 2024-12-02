from .models import CustomUser
from plants.apps.core.serializers import DynamicFieldsModelSerializer


class CustomUserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
        ]

