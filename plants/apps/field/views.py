from .models import Field
from .serializers import FieldSerializer
from .field_serializer import MyFieldSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response


class FieldViewSet(ModelViewSet):
    serializer_class = FieldSerializer
    queryset = Field.objects.select_related('created_by')


