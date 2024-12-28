# Generated by Django 5.1.2 on 2024-12-28 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('task', '0003_alter_task_deleted_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='task',
            name='aprouved',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='task',
            name='generated',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='task',
            name='frequency',
            field=models.CharField(choices=[('D', 'Daily'), ('W', 'Weekly'), ('M', 'Menstrual'), ('A', 'Annual')], max_length=1),
        ),
        migrations.AlterField(
            model_name='task',
            name='status',
            field=models.CharField(choices=[('P', 'Planed'), ('E', 'Executing...'), ('D', 'Done')], default='P', max_length=1),
        ),
    ]
