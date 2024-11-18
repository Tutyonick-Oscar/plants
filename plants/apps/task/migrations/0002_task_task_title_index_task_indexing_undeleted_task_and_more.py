# Generated by Django 5.1.2 on 2024-11-18 13:43

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field', '0002_alter_field_options_field_indexing_undeleted_fields'),
        ('task', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddIndex(
            model_name='task',
            index=models.Index(condition=models.Q(('deleted_at', None)), fields=['task_title'], name='task_title_index'),
        ),
        migrations.AddIndex(
            model_name='task',
            index=models.Index(condition=models.Q(('deleted_at', None)), fields=['deleted_at'], name='indexing_undeleted_task'),
        ),
        migrations.AddConstraint(
            model_name='task',
            constraint=models.UniqueConstraint(condition=models.Q(('deleted_at', None)), fields=('task_title', 'field'), name='one named task for a field,unless deleted'),
        ),
    ]
