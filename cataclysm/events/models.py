from django.db import models

# Create your models here.
class Event(models.Model):
    class Meta:
        app_label = 'events'
    TYPE_CHOICES = [
        ('battle','Battle'),
        ('historical','Historical'),
        ('discovery','Discovery'),
        ('event','Event'),
        ('disaster','Disaster'),
        ('meeting','Meeting'),
        ('other','Other'),
        ('in_game_event','In-Game Event'),
        ('notable','Notable'),
    ]
    name = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to='events', blank=True)
    date = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=50)
    people = models.ManyToManyField('people.Person', blank=True)
    factions = models.ManyToManyField('factions.Faction', blank=True)
    species = models.ManyToManyField('species.Species', blank=True)
    worlds = models.ManyToManyField('worlds.World', blank=True)
    event_type = models.CharField(max_length=50, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name
