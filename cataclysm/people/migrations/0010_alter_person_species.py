# Generated by Django 4.2.5 on 2024-07-20 18:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('species', '0006_alter_species_image'),
        ('people', '0009_person_agile_person_cybernetic_person_engineer_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='species',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='species.species'),
        ),
    ]
