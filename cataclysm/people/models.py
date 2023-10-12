from django.db import models

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    species = models.ForeignKey('species.Species', on_delete=models.CASCADE)
    faction = models.ForeignKey('factions.Faction', on_delete=models.SET_NULL, blank=True, null=True)
    rank = models.CharField(max_length=50, blank=True)
    position = models.CharField(max_length=50, blank=True)
    weapons = models.ManyToManyField('weapons.Weapon', blank=True)
    armors = models.ManyToManyField('armor.Armor', blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='people', blank=True)
    stats = models.ForeignKey('Statset', on_delete=models.SET_NULL, blank=True, null=True)
    skills = models.ForeignKey('Skillset', on_delete=models.SET_NULL, blank=True, null=True)
    location = models.CharField(max_length=50, blank=True)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Statset(models.Model):
    linked_person = models.OneToOneField('Person', on_delete=models.CASCADE, blank=True, null=True)
    strength = models.IntegerField()
    intelligence = models.IntegerField()
    charisma = models.IntegerField()
    dexterity = models.IntegerField()
    constitution = models.IntegerField()
    wisdom = models.IntegerField()

    def __str__(self):
        if self.linked_person:
            return f'Stats for {self.linked_person.name}'
        else:
            return 'Unlinked Stats'

class Skillset(models.Model):
    linked_person = models.OneToOneField('Person', on_delete=models.CASCADE, blank=True, null=True)
    athletics = models.IntegerField()
    acrobatics = models.IntegerField()
    bluff = models.IntegerField()
    computers = models.IntegerField()
    culture = models.IntegerField()
    disguise = models.IntegerField()
    engineering = models.IntegerField()
    intimidate = models.IntegerField()
    medicine = models.IntegerField()
    perception = models.IntegerField()
    piloting = models.IntegerField()
    sense_motive = models.IntegerField()
    life_science = models.IntegerField()
    physical_science = models.IntegerField()
    slight_of_hand = models.IntegerField()
    survival = models.IntegerField()
    stealth = models.IntegerField()
    diplomacy = models.IntegerField()

    def __str__(self):
        if self.linked_person:
            return f'Skills for {self.linked_person.name}'
        else:
            return 'Unlinked Skills'