# Generated by Django 5.1.2 on 2024-11-19 14:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("user_app", "0005_alter_customuser_password_alter_customuser_username"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="deleted_at",
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
