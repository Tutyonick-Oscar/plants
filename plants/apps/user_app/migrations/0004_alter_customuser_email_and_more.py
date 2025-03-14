# Generated by Django 5.1.2 on 2024-11-18 13:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("user_app", "0003_alter_customuser_email"),
    ]

    operations = [
        migrations.AlterField(
            model_name="customuser",
            name="email",
            field=models.EmailField(max_length=200, unique=True),
        ),
        migrations.AddIndex(
            model_name="customuser",
            index=models.Index(
                condition=models.Q(("deleted_at", None)),
                fields=["deleted_at"],
                name="indexing_undeleted_users",
            ),
        ),
        migrations.AddConstraint(
            model_name="customuser",
            constraint=models.UniqueConstraint(
                condition=models.Q(("deleted_at", None)),
                fields=("email",),
                name="unique_undeleted_user",
            ),
        ),
    ]
