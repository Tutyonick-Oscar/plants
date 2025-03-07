from django.urls import include, path, re_path

from .views import PlantDiseaseListe, PlantsCare, PlantsDetails, PlantsSpecies, plantFaq

urlpatterns = [
    path("plants-species/", PlantsSpecies.as_view(), name="plants-species"),
    path(
        "plants-details/<int:plant_id>/", PlantsDetails.as_view(), name="plants-details"
    ),
    path(
        "plants-vulnerabilities/",
        PlantDiseaseListe.as_view(),
        name="plants-vulnerabilities",
    ),
    path("plants-care/", PlantsCare.as_view(), name="plants-care-guide"),
    path("plants-article-faq/", plantFaq.as_view(), name="plants-article-faq"),
]
