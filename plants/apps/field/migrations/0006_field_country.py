# Generated by Django 5.1.2 on 2025-01-08 19:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("field", "0005_field_equipements_field_ground_ph_field_ground_type_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="field",
            name="country",
            field=models.CharField(default="DRC", max_length=50),
            preserve_default=False,
        ),
    ]
