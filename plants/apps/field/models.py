from django.db import models
from django.utils.translation import gettext_lazy as _

from plants.apps.core.models import BaseModel, CustomBaseManager


class PeriodChoices(models.TextChoices):

    SPRING = "SP", _("Spring")
    WINTER = "WI", _("Winter")
    SUMMER = "SU", _("Summer")
    AUTUMN = "AU", _("Autumn")


class GrowSpeedChoices(models.TextChoices):

    SLOW = (
        "S",
        _("Slow"),
    )
    NORMAL = "N", _("Normal")
    GOOD = "G", _("Good")
    ACCELERATE = "A", _("Acclerate")


class GroundTypeChoices(models.TextChoices):
    CLALEY = "C", _("Clayey")
    LOAMY = "L", _("Loamy")
    SANDY = "S", _("Sandy")
    CLALEY_LOAMY = "CL", _("Clayey_Loamy")


class FieldManager(CustomBaseManager):
    pass


class FieldStatusChioces(models.TextChoices):
    INITIAL = "I", _("Initial")
    GROWING = "G", _("Growing")
    HARVEST = "H", _("Harvest")
    PRODUCTION = "P", _("Production")


class Field(BaseModel):

    plant_specie = models.CharField(max_length=200)
    country = models.CharField(max_length=50)
    region = models.CharField(max_length=100)
    start_on = models.DateField(auto_now=False, auto_now_add=False)
    measure = models.FloatField()
    prod_quantity_estimated = models.FloatField()
    period = models.CharField(max_length=2, choices=PeriodChoices.choices)
    project_description = models.TextField()
    grow_speed = models.CharField(
        max_length=1, choices=GrowSpeedChoices.choices, default=GrowSpeedChoices.NORMAL
    )
    ground_ph = models.IntegerField(null=True, blank=True)
    ground_type = models.CharField(max_length=2, choices=GroundTypeChoices.choices)
    organic_materials = models.IntegerField(null=True, blank=True)
    long = models.DecimalField(decimal_places=10, max_digits=20)
    lat = models.DecimalField(decimal_places=10, max_digits=20)
    equipements = models.JSONField(null=True, blank=True)
    agroflex_advices = models.TextField(blank=True, null=True)
    status = models.CharField(
        max_length=1,
        choices=FieldStatusChioces.choices,
        default=FieldStatusChioces.INITIAL,
    )
    prod_quantity = models.FloatField(null=True, blank=True)

    objects = FieldManager()

    def get_recent_task(self):

        task = self.planed_tasks.filter(status="D").order_by("created_at").last()
        if task:
            return {
                "task_title": task.task_title,
                "frequency": task.frequency,
                "descriptions": task.descriptions,
            }

        return _("No task recently done")

    def get_field_formated_info(self):

        return {
            "plant_specie": self.plant_specie,
            "region": self.region,
            "start_on": self.start_on,
            "measure": self.measure,
            "prod_quantity_estimated": self.prod_quantity_estimated,
            "period": self.period,
            "project_description": self.project_description,
            "recent_task_done": self.get_recent_task(),
        }

    class Meta:
        indexes = [
            models.Index(
                fields=("deleted_at",),
                name="indexing_undeleted_fields",
                condition=models.Q(deleted_at=None),
            )
        ]
