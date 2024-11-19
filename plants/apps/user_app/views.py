from django.shortcuts import render
from .serializers import CreateCustomUserSerializer,CustomUserSerializer,CustomUser
from rest_framework.generics import CreateAPIView,RetrieveAPIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.core.exceptions import ValidationError


class CreateUser(CreateAPIView):
    serializer_class = CreateCustomUserSerializer
    queryset = CustomUser.objects.all()

    def create(self, request, *args, **kwargs):
        try:
            user = CreateCustomUserSerializer.create(self,validated_data=request.data)
        except ValidationError as e:
            return Response(e.error_dict)
        token,created = Token.objects.get_or_create(user = user)
        return Response({'Token' : token.key})

class UserDetails(RetrieveAPIView):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()
    