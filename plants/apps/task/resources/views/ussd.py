from rest_framework.response import Response
from rest_framework.views import APIView

from plants.apps.core.renderers import PlainTextRenderer


class GenerateUserIdent(APIView):

    renderer_classes = [PlainTextRenderer]

    def post(self, request):

        if request.content_type == "application/x-www-form-urlencoded":

            session_id = request.POST.get("sessionId")
            service_code = request.POST.get("serviceCode")
            phone_number = request.POST.get("phoneNumber")
            text = request.POST.get("text")

            if text == "":
                response = Response(data="CON Generate user ident ? \n1.Yes \n2.No")
                return response

        else:
            return Response({"message": "wrong data format"})
