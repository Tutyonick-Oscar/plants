from .models import Field
from .serializers import FieldSerializer
from rest_framework.generics import CreateAPIView

class CreateField(CreateAPIView):
    serializer_class = FieldSerializer
    queryset = Field.objects.all()
