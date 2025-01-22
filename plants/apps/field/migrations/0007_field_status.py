# Generated by Django 5.1.2 on 2025-01-22 07:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('field', '0006_field_country'),
    ]

    operations = [
        migrations.AddField(
            model_name='field',
            name='status',
            field=models.CharField(choices=[('I', 'Initial'), ('G', 'Growing'), ('H', 'Harvest'), ('P', 'Production')], default='I', max_length=1),
        ),
    ]
