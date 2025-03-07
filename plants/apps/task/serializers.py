from plants.apps.field.serializers import DynamicFieldsModelSerializer, FieldSerializer
from plants.apps.task.models import Task


class TaskSerialzer(DynamicFieldsModelSerializer):
    field = FieldSerializer(read_only=True, fields=("id", "start_on"))

    class Meta:
        model = Task
        fields = ["id", "task_title", "frequency", "descriptions", "field", "status"]
