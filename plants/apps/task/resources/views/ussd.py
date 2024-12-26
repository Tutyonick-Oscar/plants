from plants.apps.user_app.models import CustomUser
from rest_framework.views import APIView
from django.http  import HttpResponse
from rest_framework.response import Response

class GenerateUserIdent(APIView):
    
    def post(self,request):
        
        content_type = request.META.get('CONTENT_TYPE','')
        
        if 'application/x-www-form-urlencoded' in content_type:
            
            session_id = request.values.get("sessionId", None)
            service_code = request.values.get("serviceCode", None)
            phone_number = request.values.get("phoneNumber", None)
            text = request.values.get("text", "default")
            
            if text == '':
                response  = Response("CON Generate user ident ? \n1.Yes \n2.No",content_type='text/plain')
                
            return response
    
    # user = CustomUser.objects.get(username = name)
    # user_ident = '000'+str(user.pk)
    # return HttpResponse(user_ident)