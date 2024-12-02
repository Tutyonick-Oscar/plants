from .serializers import CustomUserSerializer,CustomUser
from rest_framework.viewsets import ModelViewSet
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from django.core.exceptions import ValidationError
from rest_framework.decorators import action
from plants.apps.field.field_serializer import MyFieldSerializer


class UsersViewSet(ModelViewSet):
    serializer_class = CustomUserSerializer
    queryset = CustomUser.objects.all()

    def create(self, request, *args, **kwargs):
        user = CustomUser(**request.data)
        try:
            user.full_clean()
        except ValidationError as e:
            return Response(e.error_dict)

        user.set_password(request.data["password"])
        user.save()
        token = Token.objects.create(user=user)
        return Response(
            {
                "id": user.pk,
                "username": user.username,
                "email": user.email,
                "Token": token.key,
            }
        )
    
    @action(detail=True,methods=["GET"])
    def get_fields(self,request,pk):
        user = request.user
        user_fields = user.field_set.all()
        serializer = MyFieldSerializer(user_fields,many=True,context={'request': request})
        return Response(serializer.data)
    