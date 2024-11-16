from django.shortcuts import render
from .serializers import CreateCustomUserSerializer,CustomUser
from rest_framework.generics import CreateAPIView


class CreateUser(CreateAPIView):
    serializer_class = CreateCustomUserSerializer
    queryset = CustomUser.objects.all()
