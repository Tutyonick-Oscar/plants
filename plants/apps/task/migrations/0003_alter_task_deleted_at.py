# Generated by Django 5.1.2 on 2024-11-19 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0002_task_task_title_index_task_indexing_undeleted_task_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='task',
            name='deleted_at',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]