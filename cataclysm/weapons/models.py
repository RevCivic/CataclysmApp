from django.db import models

class Weapon(models.Model):
    name = models.CharField(max_length=100)
    weapon_type = models.CharField(max_length=50)
    damage = models.CharField(max_length=20)
    critical = models.CharField(max_length=20)
    range_increment = models.IntegerField()
    capacity = models.IntegerField()
    usage = models.CharField(max_length=50)
    special_properties = models.TextField()
    secondary_weapon = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name
