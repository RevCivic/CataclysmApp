from django.db import models

# Create your models here.
class Faction(models.Model):
    class Meta:
        app_label = 'factions'
    name = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(upload_to='factions', blank=True)
    people = models.ManyToManyField('people.Person', blank=True, related_name='factions')
    species = models.ManyToManyField('species.Species', blank=True)
    worlds = models.ManyToManyField('worlds.World', blank=True)
    events = models.ManyToManyField('events.Event', blank=True)

    def __str__(self):
        return self.name
