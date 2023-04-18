# Generated by Django 2.1.2 on 2018-10-17 09:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("config_service", "0002_auto_20180731_1620"),
    ]

    operations = [
        migrations.AddField(
            model_name="securitycredential",
            name="key_to_store",
            field=models.FileField(blank=True, upload_to="media/"),
        ),
        migrations.AlterField(
            model_name="configuration",
            name="merchant_id",
            field=models.CharField(max_length=64, verbose_name="Merchant Slug"),
        ),
    ]
