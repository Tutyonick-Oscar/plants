from plants.apps.core.serializers import DynamicFieldsModelSerializer

from .models import CustomUser


class CustomUserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
        ]
