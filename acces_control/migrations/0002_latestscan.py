# Generated by Django 5.1.4 on 2025-01-12 15:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acces_control', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='LatestScan',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(blank=True, max_length=50, null=True)),
            ],
        ),
    ]
