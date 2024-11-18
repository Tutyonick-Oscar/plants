from django.db import models
from plants.apps.core.models import BaseModel,CustomBaseManager

class TaskManager(CustomBaseManager):
    pass

class Task (BaseModel):
    TASK_FREQUENCY = [
        ('day','Dayly'),
        ('week','Weekly'),
        ('mounth','Mounthly'),
        ('year','Annual')
    ]
    TASK_STATUS = [
        ('planed','Planed'),
        ('executing','Executing...'),
        ('done','Done')
    ]
    frequency = models.CharField(max_length=10,choices=TASK_FREQUENCY)
    task_title = models.CharField(max_length=200)
    descriptions = models.TextField(blank=True,null=True)
    field = models.ForeignKey('field.Field',on_delete=models.CASCADE,related_name='planed_tasks')
    status = models.CharField(max_length=50,default='planed',choices=TASK_STATUS)

    objects = TaskManager()

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
