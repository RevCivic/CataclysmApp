# Generated by Django 4.2.5 on 2023-10-11 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('species', '0001_initial'),
        ('factions', '0001_initial'),
        ('worlds', '0001_initial'),
        ('people', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='faction',
            name='people',
            field=models.ManyToManyField(blank=True, related_name='factions', to='people.person'),
        ),
        migrations.AddField(
            model_name='faction',
            name='species',
            field=models.ManyToManyField(blank=True, to='species.species'),
        ),
        migrations.AddField(
            model_name='faction',
            name='worlds',
            field=models.ManyToManyField(blank=True, to='worlds.world'),
        ),
    ]