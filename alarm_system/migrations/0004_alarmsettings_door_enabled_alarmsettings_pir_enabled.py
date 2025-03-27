# Generated by Django 5.1.4 on 2025-01-12 20:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('alarm_system', '0003_alarmsettings_arming_start_time_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='alarmsettings',
            name='door_enabled',
            field=models.BooleanField(default=True),
        ),
        migrations.AddField(
            model_name='alarmsettings',
            name='pir_enabled',
            field=models.BooleanField(default=True),
        ),
    ]
