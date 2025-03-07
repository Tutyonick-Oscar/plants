from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from plants.apps.task.serializers import Task, TaskSerialzer


class CreateTask(GenericAPIView):

    def post(self, request, field_id):

        user = request.user
        try:
            field = user.field_set.get(pk=field_id)
        except Exception as e:
            return Response({"message": "no field match the given query !"})

        request.data["field"] = field
        task = Task(**request.data)
        task.save()
        serializer = TaskSerialzer(task, context={"request": request})

        return Response(serializer.data)


class TaskNotification:
    pass
