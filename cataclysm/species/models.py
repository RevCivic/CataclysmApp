from django.db import models

class Species(models.Model):
    class Meta:
        app_label = 'species'
    SIZE_CHOICES = [
        ('diminutive', 'Diminutive'),
        ('tiny', 'Tiny'),
        ('small', 'Small'),
        ('medium', 'Medium'),
        ('large', 'Large'),
        ('huge', 'Huge'),
        ('gargantuan', 'Gargantuan'),
        ('colossal', 'Colossal'),
        ('planetary', 'Planetary'),
    ]
    TYPE_CHOICES = [
        ('animal','Animal'),
        ('biotech','Bio-Tech'),
        ('plant','Plant'),
        ('metamorph','Metamorph'),
        ('unique','Unique'),
    ]
    AIR_CHOICES = [
        ('oxygen','Oxygen'),
        ('nitrogen','Nitrogen'),
        ('carbon-dioxide','Carbon Dioxide'),
        ('argon','Argon'),
        ('unique','Unique'),
        ('xenon','Xenon'),
        ('dihydrogen-oxide','Dihydrogen Oxide'),
        ('hydrogen','Hydrogen'),
        ('helium','Helium'),
        ('neon','Neon'),
    ]
    REPRODUCTIVE_CHOICES = [
        ('standard','Standard'),
        ('asexual','Asexual'),
        ('fission','Fission'),
        ('clone','Clone'),
        ('unique','Unique'),
    ]
    GRAVITY_CHOICES = [
        ('light','Light'),
        ('standard','Standard'),
        ('heavy','Heavy'),
    ]
    ACCORD_STATUS_CHOICES = [
        ('founder','Founding Member'),
        ('ally','Ally'),
        ('member','Member'),
        ('peace','Peace Treaty'),
        ('enemy','Enemy'),
        ('nuetral','Nuetral'),
        ('unknown','Unknown'),
        ('undiscovered','Undiscovered'),
    ]
    SOCIETY_CHOICES = [
        ('monarchy','Monarchy'),
        ('theocracy','Theocracy'),
        ('democracy','Democracy'),
        ('caste','Caste'),
        ('tribal','Tribal'),
        ('free','Free'),
        ('unknown','Unknown'),
        ('empire','Empire'),
        ('conglomerate','Conglomerate'),
        ('aristocracy','Aristocracy'),
        ('multiple','Multiple'),
        ('anarchy','Anarchy'),
        ('technocracy','Technocracy'),
    ]
    LOCOMOTION_CHOICES = [
        ('bipedal','Bipedal'),
        ('tentacle','Tentacle'),
        ('multiped','Multiped'),
        ('flight','Flight'),
        ('serpentine','Serpentine'),
        ('metamorph','Metamorph'),
        ('float','Float'),
        ('quadruped','Quadruped'),
        ('octoped','Octoped'),
    ]
    name = models.CharField(max_length=100)
    home_world = models.CharField(max_length=100, blank=True, null=True)
    society = models.CharField(max_length=50, choices=SOCIETY_CHOICES, blank=True, null=True)
    accord_status = models.CharField(max_length=20, choices=ACCORD_STATUS_CHOICES, blank=True, null=True)
    background = models.TextField(blank=True, null=True)
    sociology = models.TextField(blank=True, null=True)
    physiology = models.TextField(blank=True, null=True)
    racial_traits = models.JSONField(blank=True, null=True)
    size = models.CharField(max_length=20, choices=SIZE_CHOICES, blank=True, null=True)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES, blank=True, null=True)
    air = models.CharField(max_length=50, choices=AIR_CHOICES, blank=True, null=True)
    reproduction_method = models.CharField(max_length=20, choices=REPRODUCTIVE_CHOICES, blank=True, null=True)
    hours_of_sleep = models.IntegerField(null=True, blank=True)
    days_without_food = models.IntegerField(null=True, blank=True)
    days_without_water = models.IntegerField(null=True, blank=True)
    strength_rating = models.IntegerField(null=True, blank=True)
    toughness_rating = models.IntegerField(null=True, blank=True)
    speed_rating = models.IntegerField(null=True, blank=True)
    intelligence_rating = models.IntegerField(null=True, blank=True)
    natural_weapons = models.BooleanField(default=False)
    natural_armor = models.BooleanField(default=False)
    can_fly = models.BooleanField(default=False)
    aquatic = models.BooleanField(default=False)
    amphibious = models.BooleanField(default=False)
    telepathic = models.BooleanField(default=False)
    psionic = models.BooleanField(default=False)
    gravity = models.CharField(max_length=15, choices=GRAVITY_CHOICES, blank=True, null=True)
    special_abilities = models.JSONField(blank=True, null=True)
    locomotion_method = models.CharField(max_length=20, choices=LOCOMOTION_CHOICES, blank=True, null=True)
    image = models.ImageField(upload_to='species/images/', null=True, blank=True)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name