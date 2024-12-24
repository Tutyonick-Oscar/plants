from plants.apps.user_app.models import CustomUser
from django.db.models import F
from django.http import HttpResponse

def generate_user_ident(request):
    session_id = request.values.get("sessionId", None)
    service_code = request.values.get("serviceCode", None)
    phone_number = request.values.get("phoneNumber", None)
    text = request.values.get("text", "default")
    
    if text == '':
        response  = HttpResponse("CON Generate user ident \n")
        
    return response
    # user = CustomUser.objects.get(username = name)
    # user_ident = '000'+str(user.pk)
    # return HttpResponse(user_ident)