# Generated by Django 4.2.5 on 2024-07-21 01:38

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('people', '0011_personimage_person_additional_images'),
    ]

    operations = [
        migrations.RenameField(
            model_name='personimage',
            old_name='image',
            new_name='additional_image',
        ),
    ]