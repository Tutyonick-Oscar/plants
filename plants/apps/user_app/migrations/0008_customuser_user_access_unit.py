# Generated by Django 5.1.2 on 2025-01-22 07:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_app", "0007_customuser_role"),
    ]

    operations = [
        migrations.AddField(
            model_name="customuser",
            name="user_access_unit",
            field=models.DecimalField(decimal_places=4, default=0.0, max_digits=16),
        ),
    ]
