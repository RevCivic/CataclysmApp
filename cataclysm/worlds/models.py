from django.db import models

class World(models.Model):
    name = models.CharField(max_length=50)
    system = models.CharField(max_length=50)
    planet_class = models.CharField(max_length=2)
    colonized = models.BooleanField()
    terraformed = models.BooleanField()
    contains_flora = models.BooleanField()
    contains_fauna = models.BooleanField()
    contains_sentient_life = models.BooleanField()
    special_traits = models.JSONField()


    def __str__(self):
        return self.name
