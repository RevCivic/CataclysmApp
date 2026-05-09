from django.db import models


class Species(models.Model):
    class Meta:
        app_label = 'species'

    species_name = models.CharField(max_length=100)
    home_world = models.CharField(max_length=100, blank=True, null=True)
    size = models.CharField(max_length=50, blank=True, null=True)
    type = models.CharField(max_length=50, blank=True, null=True)
    air = models.CharField(max_length=50, blank=True, null=True)
    sex = models.CharField(max_length=50, blank=True, null=True)
    strength = models.IntegerField(null=True, blank=True)
    natural_weapon = models.BooleanField(default=False)
    toughness = models.IntegerField(null=True, blank=True)
    natural_armor = models.BooleanField(default=False)
    speed = models.IntegerField(null=True, blank=True)
    intelligence = models.IntegerField(null=True, blank=True)
    flier = models.BooleanField(default=False)
    aquatic = models.BooleanField(default=False)
    amphibious = models.BooleanField(default=False)
    tech_level = models.CharField(max_length=50, blank=True, null=True)
    telepathic = models.BooleanField(default=False)
    psionic = models.BooleanField(default=False)
    light_grav = models.BooleanField(default=False)
    heavy_grav = models.BooleanField(default=False)
    status = models.CharField(max_length=50, blank=True, null=True)
    locomotion = models.CharField(max_length=50, blank=True, null=True)
    society = models.TextField(blank=True, null=True)
    attributes = models.JSONField(blank=True, null=True)
    hours_of_sleep = models.IntegerField(null=True, blank=True)
    days_without_food = models.IntegerField(null=True, blank=True)
    days_without_water = models.IntegerField(null=True, blank=True)
    background = models.TextField(blank=True, null=True)
    sociology = models.TextField(blank=True, null=True)
    physiology = models.TextField(blank=True, null=True)
    special_abilities = models.JSONField(blank=True, null=True)
    match_status = models.CharField(max_length=50, blank=True, null=True)
    image = models.ImageField(upload_to='species/images/', null=True, blank=True)
    hidden = models.BooleanField(default=False)

    @property
    def name(self):
        return self.species_name


    def __str__(self):
        return self.species_name
