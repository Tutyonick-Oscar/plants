from django.urls import path,re_path,include
from .views import PlantsSpecies,PlantsDetails,PlantDiseaseListe,PlantsCare,plantFaq
from plants.settings.settings import PERENUAL_API_KEY

urlpatterns = [
    path('plants-species/',PlantsSpecies.as_view(),name="plants-species"),
    path(
        'plants-details/<int:plant_id>/',
        PlantsDetails.as_view(),
        name="plants-details"
    ),
    path('plants-vulnerabilities/',PlantDiseaseListe.as_view(),name="plants-vulnerabilities"),
    path('plants-care/',PlantsCare.as_view(),name="plants-care-guide"),
    path('plants-article-faq/',plantFaq.as_view(),name="plants-article-faq"),
]