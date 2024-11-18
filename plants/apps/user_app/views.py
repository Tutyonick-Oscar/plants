from django.shortcuts import render
from .serializers import CreateCustomUserSerializer,CustomUser
from rest_framework.generics import CreateAPIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


class CreateUser(CreateAPIView):
    serializer_class = CreateCustomUserSerializer
    queryset = CustomUser.objects.all()

    def create(self, request, *args, **kwargs):
        user = CreateCustomUserSerializer.create(self,validated_data=request.data)
        token,created = Token.objects.get_or_create(user = user)
        return Response({'Token' : token.key})