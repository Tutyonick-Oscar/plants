from rest_framework.generics import GenericAPIView
from plants.apps.core.models import RequestOffset
from rest_framework.response import Response
from rest_framework.decorators import api_view


@api_view(['POST'])
def init_request_offset(self,request):
    offset = RequestOffset()
    offset.save()
    return Response({'success' : f'offset initialized to {offset.offset} successfuly !'})