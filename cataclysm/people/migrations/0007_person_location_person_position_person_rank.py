# Generated by Django 4.2.5 on 2023-10-11 23:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0006_person_hidden'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='location',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='person',
            name='position',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='person',
            name='rank',
            field=models.CharField(blank=True, max_length=50),
        ),
    ]
