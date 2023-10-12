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
    home_world = models.CharField(max_length=100)
    society = models.CharField(max_length=50, choices=SOCIETY_CHOICES)
    accord_status = models.CharField(max_length=20, choices=ACCORD_STATUS_CHOICES)
    background = models.TextField()
    sociology = models.TextField()
    physiology = models.TextField()
    racial_traits = models.JSONField()
    size = models.CharField(max_length=20, choices=SIZE_CHOICES)
    type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    air = models.CharField(max_length=50, choices=AIR_CHOICES)
    reproduction_method = models.CharField(max_length=20, choices=REPRODUCTIVE_CHOICES)
    hours_of_sleep = models.IntegerField()
    days_without_food = models.IntegerField()
    days_without_water = models.IntegerField()
    strength_rating = models.IntegerField()
    toughness_rating = models.IntegerField()
    speed_rating = models.IntegerField()
    intelligence_rating = models.IntegerField()
    natural_weapons = models.BooleanField()
    natural_armor = models.BooleanField()
    can_fly = models.BooleanField()
    aquatic = models.BooleanField()
    amphibious = models.BooleanField()
    telepathic = models.BooleanField()
    psionic = models.BooleanField()
    gravity = models.CharField(max_length=15, choices=GRAVITY_CHOICES)
    special_abilities = models.JSONField()
    locomotion_method = models.CharField(max_length=20, choices=LOCOMOTION_CHOICES)
    image = models.ImageField(upload_to='species/images/', null=True, blank=True)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name