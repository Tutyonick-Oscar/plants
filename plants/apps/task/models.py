from django.db import models
from django.utils.translation import gettext_lazy as _
from plants.apps.core.models import BaseModel,CustomBaseManager

class TaskManager(CustomBaseManager):
    pass

class TaskFrequencyChoices(models.TextChoices):
    DAILY = 'D',_('Daily')
    WEEKLY = 'W',_('Weekly')
    MENSTRUAL = 'M',_('Menstrual')
    ANNUAL = 'A',_('Annual')
    
class TaskStatusChoices(models.TextChoices):
    PLANED = 'P',_('Planed')
    EXECUTE = 'E',_('Executing...')
    DONE = 'D',_('Done')

class Task (BaseModel):
    frequency = models.CharField(max_length=1,choices=TaskFrequencyChoices.choices)
    task_title = models.CharField(max_length=200)
    descriptions = models.TextField(blank=True,null=True)
    field = models.ForeignKey('field.Field',on_delete=models.CASCADE,related_name='planed_tasks')
    status = models.CharField(max_length=1,default='P',choices=TaskStatusChoices.choices)
    generated = models.BooleanField(default=False)
    aprouved = models.BooleanField(default=False)

    objects = TaskManager()
    
    def suggest_field_task(self):
        field_info = self.field.get_field_formated_info()
        #process AI task creation
    
    def __str__(self):
        return self.task_title

    class Meta :
        constraints = [
            models.UniqueConstraint(
                fields=['task_title','field'],
                name="one named task for a field,unless deleted",
                condition=models.Q(deleted_at=None)
            )
        ]
        indexes = [
            models.Index(
                fields=('task_title',),
                name='task_title_index',
                condition=models.Q(deleted_at=None)
            ),
            models.Index(
                fields=('deleted_at',),
                name='indexing_undeleted_task',
                condition=models.Q(deleted_at=None)
            )
        ]
