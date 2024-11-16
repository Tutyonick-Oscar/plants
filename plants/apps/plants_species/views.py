from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from plants.settings.settings import PERENUAL_API_KEY
import requests
from django.views.decorators.csrf import csrf_exempt

class PlantsSpecies(GenericAPIView): 
    
    base_url = "https://perenual.com/api/"
    end_url = f"species-list"

    headers = {'method':'GET',"Accept":'application/json'}

    def get(self,request,plant_id=None):

        if plant_id is not None:
            self.end_url+=f'/{plant_id}'

        query_params = ''
        complet_url = self.base_url+self.end_url+f"?key={PERENUAL_API_KEY}"

        if len(request.query_params)>0:
            for param in request.query_params:
                query_params += f'&{param}={request.query_params[param]}'

            complet_url +=query_params

        response = requests.get(complet_url,self.headers)
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

class plantFaq (PlantsSpecies):
    end_url = "article-faq-list"