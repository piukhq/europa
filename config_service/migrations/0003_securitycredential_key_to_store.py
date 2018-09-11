# Generated by Django 2.1.1 on 2018-09-07 09:35

import config_service.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('config_service', '0002_auto_20180731_1620'),
    ]

    operations = [
        migrations.AddField(
            model_name='securitycredential',
            name='key_to_store',
            field=models.FileField(blank=True, upload_to='', validators=[config_service.models.read_file_contents]),
        ),
    ]
