from rest_framework import status
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from agroflex.apps.field.models import Field
from agroflex.apps.old_market.serializers.product import Product, ProductSerializer
from agroflex.apps.old_market.utils.cost import product_access_unit_cost


class ProductViewSet(ModelViewSet):

    serializer_class = ProductSerializer
    queryset = Product.objects.select_related("created_by", "product_field").filter(
        product_on_sale=True
    )

    def create(self, request, *args, **kwargs):
        # return super().create(request, *args, **kwargs)
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        cost = product_access_unit_cost(
            serializer.validated_data.get("product_measurement_unit"),
            serializer.validated_data.get("product_quantity"),
        )

        user = self.request.user
        if user.user_access_unit < cost:
            print("operation imposible")
            return Response(
                {
                    "success": False,
                    "respose_code": 403,
                    "respose_data": None,
                    "response_message": "insufficient AU, please charge your account",
                },
                status=403,
            )
        user.user_access_unit -= cost
        user.save()
        serializer.save()
        return Response(
            {
                "success": True,
                "response_code": status.HTTP_201_CREATED,
                "response_data": serializer.data,
                "response_messsage": "product created successfuly",
            }
        )


class FieldProductView(GenericAPIView):
    serializer_class = ProductSerializer
    queryset = Product.objects.select_related("created_by", "product_field").filter(
        product_on_sale=True
    )

    def post(self, request, field_pk):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            field = Field.objects.get(id=field_pk)
        except Field.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "respose_code": 404,
                    "respose_data": None,
                    "response_message": f"field with id {field_pk} does not exist",
                },
                status=404,
            )
        cost = product_access_unit_cost(
            serializer.validated_data.get("product_measurement_unit"),
            serializer.validated_data.get("product_quantity"),
        )
        user = request.user
        if user.user_access_unit < cost:
            return Response(
                {
                    "success": False,
                    "respose_code": 403,
                    "respose_data": None,
                    "response_message": "insufficient AU, please charge your account",
                },
                status=403,
            )
        user.user_access_unit -= cost
        user.save()
        field.products.create(**serializer.validated_data)
        return Response(
            {
                "success": True,
                "response_code": status.HTTP_201_CREATED,
                "response_data": serializer.data,
                "response_messsage": "product created successfuly",
            }
        )
