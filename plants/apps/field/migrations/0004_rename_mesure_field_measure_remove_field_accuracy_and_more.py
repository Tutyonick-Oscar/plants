# Generated by Django 5.1.2 on 2024-12-28 15:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("field", "0003_alter_field_deleted_at"),
    ]

    operations = [
        migrations.RenameField(
            model_name="field",
            old_name="mesure",
            new_name="measure",
        ),
        migrations.RemoveField(
            model_name="field",
            name="accuracy",
        ),
        migrations.AddField(
            model_name="field",
            name="agroflex_advices",
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="field",
            name="grow_speed",
            field=models.CharField(
                choices=[
                    ("S", "Slow"),
                    ("N", "Normal"),
                    ("G", "Good"),
                    ("A", "Acclerate"),
                ],
                default="N",
                max_length=1,
            ),
        ),
        migrations.AddField(
            model_name="field",
            name="period",
            field=models.CharField(
                choices=[
                    ("SP", "Spring"),
                    ("wI", "Winter"),
                    ("SU", "Summer"),
                    ("AU", "Autumn"),
                ],
                default="SU",
                max_length=2,
            ),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="field",
            name="prod_quantity_estimated",
            field=models.FloatField(default=20.5),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name="field",
            name="project_description",
            field=models.TextField(default="descriptions"),
            preserve_default=False,
        ),
    ]
