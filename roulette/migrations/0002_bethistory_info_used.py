# Generated by Django 5.0.2 on 2024-05-20 19:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('roulette', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='bethistory',
            name='info_used',
            field=models.BooleanField(default=False),
        ),
    ]
