from django.db import models
from django.utils.translation import gettext_lazy as _

from plants.apps.core.models import BaseModel, CustomBaseManager


class ProductManager(CustomBaseManager): ...


class Product(BaseModel):

    class MeasurementUnitsChoices(models.TextChoices):
        KILOGRAM = "Kg", _("Kilogram")
        TONNE = "T", _("Tonne")

    product_field = models.ForeignKey(
        "field.Field",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="products",
    )
    product_name = models.CharField(max_length=120)
    product_type = models.CharField(max_length=120)
    product_country = models.CharField(max_length=50)
    product_region = models.CharField(max_length=120)
    product_quantity = models.DecimalField(max_digits=6, decimal_places=2)
    product_measurement_unit = models.CharField(
        max_length=3,
        choices=MeasurementUnitsChoices.choices,
        default=MeasurementUnitsChoices.KILOGRAM,
    )
    product_price = models.DecimalField(max_digits=16, decimal_places=4)
    product_on_sale = models.BooleanField(default=False)

    objects = ProductManager()

    class Meta: ...
