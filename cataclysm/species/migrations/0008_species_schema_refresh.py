from django.db import migrations, models


def migrate_gravity_flags(apps, schema_editor):
    Species = apps.get_model('species', 'Species')
    species_to_update = []
    for species in Species.objects.all():
        gravity = getattr(species, 'gravity', None)
        species.light_grav = gravity == 'light'
        species.heavy_grav = gravity == 'heavy'
        species_to_update.append(species)
    if species_to_update:
        Species.objects.bulk_update(species_to_update, ['light_grav', 'heavy_grav'])


class Migration(migrations.Migration):

    dependencies = [
        ('species', '0007_alter_species_accord_status_alter_species_air_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='species',
            old_name='name',
            new_name='species_name',
        ),
        migrations.RenameField(
            model_name='species',
            old_name='strength_rating',
            new_name='strength',
        ),
        migrations.RenameField(
            model_name='species',
            old_name='natural_weapons',
            new_name='natural_weapon',
        ),
        migrations.RenameField(
            model_name='species',
            old_name='toughness_rating',
            new_name='toughness',
        ),
        migrations.RenameField(
            model_name='species',
            old_name='speed_rating',
            new_name='speed',
        ),
        migrations.RenameField(
            model_name='species',
            old_name='intelligence_rating',
            new_name='intelligence',
        ),
        migrations.RenameField(
            model_name='species',
            old_name='can_fly',
            new_name='flier',
        ),
        migrations.RenameField(
            model_name='species',
            old_name='accord_status',
            new_name='status',
        ),
        migrations.RenameField(
            model_name='species',
            old_name='locomotion_method',
            new_name='locomotion',
        ),
        migrations.RenameField(
            model_name='species',
            old_name='racial_traits',
            new_name='attributes',
        ),
        migrations.AddField(
            model_name='species',
            name='sex',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='species',
            name='tech_level',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='species',
            name='light_grav',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='species',
            name='heavy_grav',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='species',
            name='match_status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.RunPython(migrate_gravity_flags, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='species',
            name='reproduction_method',
        ),
        migrations.RemoveField(
            model_name='species',
            name='gravity',
        ),
        migrations.AlterField(
            model_name='species',
            name='species_name',
            field=models.CharField(max_length=100),
        ),
        migrations.AlterField(
            model_name='species',
            name='size',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='species',
            name='type',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='species',
            name='air',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='species',
            name='status',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='species',
            name='locomotion',
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AlterField(
            model_name='species',
            name='society',
            field=models.TextField(blank=True, null=True),
        ),
    ]
