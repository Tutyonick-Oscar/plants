import threading
from re import sub

from django.http import HttpResponse
from django.urls import resolve
from rest_framework.authtoken.models import Token

local = threading.local()

def get_user(request):

    header_token = request.META.get("HTTP_AUTHORIZATION", None)
    if header_token is not None:
        try:
            token = sub("Token ", "", header_token)
            token_obj = Token.objects.get(key=token)
            request.user = token_obj.user
        except Token.DoesNotExist:
            pass


class PlantsMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        get_user(request)
        view_name = resolve(request.path_info).view_name
        local.CURRENT_USER = request.user

        # exclude login views
        # if view_name != "api-login" and view_name != "user_app:api-login":
        #     try:
        #         if request.user.banned:
        #             return HttpResponse("any request allowed !")

        #     except AttributeError:
        #         pass

        response = self.get_response(request)

        return response
