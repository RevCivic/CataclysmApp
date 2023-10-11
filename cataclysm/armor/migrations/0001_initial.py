# Generated by Django 4.2.5 on 2023-10-11 01:25

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Armor',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('armor_type', models.CharField(max_length=50)),
                ('base_armor_class', models.IntegerField()),
                ('max_dexterity_bonus', models.IntegerField()),
                ('armor_check_penalty', models.IntegerField()),
                ('speed_penalty', models.IntegerField()),
                ('weight', models.DecimalField(decimal_places=2, max_digits=5)),
                ('description', models.TextField()),
                ('dynamic_tags', models.JSONField(blank=True, null=True)),
            ],
        ),
    ]
