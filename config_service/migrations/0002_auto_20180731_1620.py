# Generated by Django 2.0.7 on 2018-07-31 16:20

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("config_service", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="configuration",
            name="handler_type",
            field=models.IntegerField(
                choices=[
                    (0, "Update"),
                    (1, "Join"),
                    (2, "Validate"),
                    (3, "Transaction Matching"),
                ]
            ),
        ),
    ]
