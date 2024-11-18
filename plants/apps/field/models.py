from django.db import models
from plants.apps.core.models import BaseModel,CustomBaseManager

class FieldManager(CustomBaseManager):
    pass

class Field(BaseModel):
    plant_specie = models.CharField(max_length=200)
    region = models.CharField(max_length=100)
    start_on = models.DateField(auto_now=False,auto_now_add=False)
    mesure = models.FloatField()
    accuracy = models.FloatField(default=0.00)

    objects = FieldManager()

    class Meta:
        indexes = [
            models.Index(
                fields=('deleted_at',),
                name='indexing_undeleted_fields',
                condition=models.Q(deleted_at=None)
            )
        ]



