from django.db import models

class Armor(models.Model):
    name = models.CharField(max_length=100)
    armor_type = models.CharField(max_length=50)
    base_armor_class = models.IntegerField()
    max_dexterity_bonus = models.IntegerField()
    armor_check_penalty = models.IntegerField()
    speed_penalty = models.IntegerField()
    weight = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField()
    # JSON field for dynamic tags
    dynamic_tags = models.JSONField(blank=True, null=True)

    def __str__(self):
        return self.name