from plants.apps.core.serializers import DynamicFieldsModelSerializer
from plants.apps.task.serializers import TaskSerialzer

from .models import Field


class MyFieldSerializer(DynamicFieldsModelSerializer):
    planed_tasks = TaskSerialzer(
        read_only=True,
        many=True,
        fields=("id", "frequency", "task_title", "descriptions", "status"),
    )

    class Meta:
        model = Field
        fields = [
            "id",
            "plant_specie",
            "region",
            "start_on",
            "mesure",
            "accuracy",
            "planed_tasks",
        ]
