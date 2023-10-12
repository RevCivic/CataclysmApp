# Generated by Django 4.2.5 on 2023-10-11 16:20

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('factions', '0002_initial'),
        ('people', '0002_alter_person_bio_alter_person_faction_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='faction',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='factions.faction'),
        ),
        migrations.AlterField(
            model_name='person',
            name='skills',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='people.skills'),
        ),
        migrations.AlterField(
            model_name='person',
            name='stats',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='people.stats'),
        ),
    ]