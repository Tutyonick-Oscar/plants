import json

import requests
from rest_framework.decorators import action
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from plants.apps.agent.main import create_agricultural_project
from plants.settings.settings import THINGSPEAK_BASE_API_URL

from .forms.init_field import InitFieldForm
from .models import Field
from .serializers import FieldSerializer


class FieldViewSet(ModelViewSet):
    serializer_class = FieldSerializer
    queryset = Field.objects.select_related("created_by")

    @action(detail=False, methods=["post"])
    def init_field_request(self, request, *args, **kwargs):
        form = InitFieldForm(json.loads(request.body))

        if form.is_valid():
            for period in ["SPRING", "WINTER", "SUMMER", "AUTUMN"]:
                if form.data.get("period") in period:
                    form.data["period"] = period

            for ground_type in ["CLALEY", "LOAMY", "SANDY", "CLALEY_LOAMY"]:
                if form.data.get("ground_type") in ground_type:
                    form.data["ground_type"] = ground_type

            project = create_agricultural_project(
                {
                    "objective": form.data.get("project_description"),
                    "country": form.data.get("country"),
                    "location": form.data.get("region"),
                }
            )

            return Response(project)

        return Response(dict(form.errors), status=402)


class FieldMonitoringView(GenericAPIView):
    def post(self, request, field_id):
        try:
            field = Field.objects.get(pk=field_id)
        except Field.DoesNotExist:
            return Response(
                {"message": f"the field with id {field_id} does not exist"}, status=404
            )
        # get IOT json data (currently get thingspeak api data)
        headers = {"method": "GET", "Accept": "application/json"}
        response = requests.get(
            THINGSPEAK_BASE_API_URL + "feeds/last.json", headers=headers
        )
        # get field data
        field_data = field.get_field_formated_info()
        res_data = response.json()

        formated_data = {
            "temperature": res_data.get("field1"),
            "humidity": res_data.get("field2"),
            "illuminance": res_data.get("field3"),
            "soil_moisture": res_data.get("field4"),
            "soil_salinity": res_data.get("field5"),
            "battery_voltage": res_data.get("field6"),
        }

        # process AI data analyse...

        return Response({"field": field_data, "agro_iot_info": formated_data})
