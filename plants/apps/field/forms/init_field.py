from django.forms import ModelForm

from ..models import Field


class InitFieldForm(ModelForm):

    class Meta:
        model = Field
        fields = [
            "plant_specie",
            "country",
            "region",
            "start_on",
            "measure",
            "prod_quantity_estimated",
            "period",
            "project_description",
            "ground_ph",
            "ground_type",
            "organic_materials",
            "long",
            "lat",
            "equipements",
        ]
