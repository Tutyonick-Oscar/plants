from rest_framework.generics import GenericAPIView
from plants.apps.core.models import RequestOffset
from rest_framework.response import Response


class InitRequestOffset(GenericAPIView):
    def post(self,request):
        offset = RequestOffset()
        offset.save()
        return Response({'success' : f'offset initialized to {offset.offset} successfuly !'})