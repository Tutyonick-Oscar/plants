from django.contrib.auth.models import User
from rest_framework import serializers
from .models import CustomUser, CustomUserManager
from plants.apps.core.serializers import DynamicFieldsModelSerializer
from rest_framework.authtoken.models import Token


class CustomUserSerializer(DynamicFieldsModelSerializer):
    class Meta:
        model = CustomUser
        fields = [
            "id",
            "username",
            "email",
        ]


class CreateCustomUserSerializer(serializers.ModelSerializer, CustomUserManager):

    class Meta:
        model = CustomUser
        fields = ["password", "username", "email"]

    def create(self, validated_data):
        user = CustomUser(**validated_data)
        user.set_password(validated_data["password"])
        user.save()
        return user
