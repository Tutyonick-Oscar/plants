# Generated by Django 5.1.2 on 2025-01-22 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user_app', '0006_alter_customuser_deleted_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='customuser',
            name='role',
            field=models.CharField(choices=[('M', 'Marchant'), ('F', 'Farmer'), ('S', 'Simple_user')], default='S', max_length=1),
        ),
    ]
