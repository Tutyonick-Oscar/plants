from datetime import datetime

from django.db import models

from plants.apps.core.middlewares import local
from plants.settings.settings import AUTH_USER_MODEL


class CustomQueryset(models.QuerySet):

    def delete(self):
        return self.update(deleted_at=datetime.now())


class CustomBaseManager(models.Manager):

    def get_queryset(self) -> models.QuerySet:
        return CustomQueryset(model=self.model, using=self._db).filter(deleted_at=None)

    # def delete(self) :
    #     return self.get_queryset().delete()


class BaseModel(models.Model):

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        AUTH_USER_MODEL, on_delete=models.CASCADE, blank=True
    )
    deleted_at = models.DateTimeField(blank=True,default=None, null=True)

    objects = CustomBaseManager()

    class Meta:
        abstract = True
        base_manager_name = "objects"
        default_manager_name = "objects"

    def delete(self, **kwargs):

        if self.pk is None:
            raise ValueError(
                "%s object can't be deleted because its %s attribute is set "
                "to None." % (self._meta.object_name, self._meta.pk.attname)
            )
        self.deleted_at = datetime.now()
        self.save()
        return self

    def save(self, *args, **kwargs):
        self.created_by = getattr(local, "CURRENT_USER")
        super().save(*args, **kwargs)
        return self

class RequestOffset(BaseModel):
    created_by = None
    offset = models.IntegerField(default=0)