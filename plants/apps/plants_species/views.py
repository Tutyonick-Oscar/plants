import requests
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from plants.apps.core.models import RequestOffset
from plants.settings.settings import PERENUAL_API_KEYS


class PlantsSpecies(GenericAPIView):

    base_url = "https://perenual.com/api/"
    end_url = f"species-list"

    headers = {"method": "GET", "Accept": "application/json"}

    def get(self, request, plant_id=None):

        request_offset = RequestOffset.objects.first().offset

        if plant_id is not None:
            self.end_url += f"/{plant_id}"

        query_params = ""

        # db offest must be equal to list keys in PERENUAL_API_KEYS
        try:
            complet_url = (
                self.base_url
                + self.end_url
                + f"?key={PERENUAL_API_KEYS[request_offset]}"
            )
        except IndexError:
            off = RequestOffset.objects.first()
            off.offset = 0
            off.save()
            complet_url = (
                self.base_url
                + self.end_url
                + f"?key={PERENUAL_API_KEYS[request_offset]}"
            )

        # handling query parameters
        if len(request.query_params) > 0:
            for param in request.query_params:
                query_params += f"&{param}={request.query_params[param]}"

            complet_url += query_params

        response = requests.get(complet_url, self.headers)

        # handling retelimit of api  access

        if response.headers.get("X-RateLimit-Remaining") is not None:
            if int(response.headers["X-RateLimit-Remaining"]) == 1:
                off = RequestOffset.objects.first()
                off.offset = request_offset + 1
                off.save()

        if response.json().get("X-RateLimit-Remaining") is not None:
            return Response({"message": "limit offset"})

        return Response(response.json())


class PlantsDetails(PlantsSpecies):

    end_url = "species/details"


"""
    liste des maladies des plantes
"""


class PlantDiseaseListe(PlantsSpecies):
    end_url = "pest-disease-list"


class PlantsCare(PlantsSpecies):
    end_url = "species-care-guide-list"


# class PlantsMap(PlantsSpecies):
#     end_url = "hardiness-map"


class plantFaq(PlantsSpecies):
    end_url = "article-faq-list"
