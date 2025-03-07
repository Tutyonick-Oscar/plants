import threading
import traceback
from re import sub

from django.http import HttpResponse
from django.urls import resolve
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response

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


class AuthUserMiddleware:
    """setting user to request
    this class is used to associate the user to the incoming request
    so that we can easely get the current user in all application parts by calling the CURRENT_USER
    attribute of local object (threading).
    a usefull exemple of this is in the apps.core.model.BaseModel class
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):

        get_user(request)
        view_name = resolve(request.path_info).view_name
        local.CURRENT_USER = request.user

        response = self.get_response(request)

        return response


class ExceptionHandlerMiddleware:
    """uncaught exceptions handler
    this class is used to handle all uncaught exceptions, severaly exceptions of type 500
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request, *args, **kwds):

        response = self.get_response(request)
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        try:
            response.render()
        except Exception:
            ...

        return response

    def process_exception(self, request, exception):

        error_message = str(exception)

        print(
            "==================================== Exception =========================================="
        )
        print(error_message)
        print(traceback.format_exc())
        print(
            "==================================== End Exception ========================================"
        )
        response = Response(
            {
                "success": False,
                "response_code": 500,
                "response_data": None,
                "response_message": f"ERROR : {error_message}",
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        response.accepted_renderer = JSONRenderer()
        response.accepted_media_type = "application/json"
        response.renderer_context = {}
        response.render()
        return response
