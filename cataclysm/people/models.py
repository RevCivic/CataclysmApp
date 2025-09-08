from django.db import models


class Trait(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    sex = models.CharField(max_length=50, default='None')
    species = models.ForeignKey('species.Species', on_delete=models.CASCADE, blank=True, null=True)
    faction = models.ForeignKey('factions.Faction', on_delete=models.SET_NULL, blank=True, null=True)
    rank = models.CharField(max_length=50, blank=True)
    position = models.CharField(max_length=50, blank=True)
    weapons = models.ManyToManyField('weapons.Weapon', blank=True)
    armors = models.ManyToManyField('armor.Armor', blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='people/images/', blank=True)
    stats = models.ForeignKey('Statset', on_delete=models.SET_NULL, blank=True, null=True)
    skills = models.ForeignKey('Skillset', on_delete=models.SET_NULL, blank=True, null=True)
    traits = models.ManyToManyField('Trait', blank=True)
    location = models.CharField(max_length=50, blank=True)
    additional_images = models.ManyToManyField('PersonImage', blank=True)
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
        

class PersonImage(models.Model):
    linked_person = models.ForeignKey('Person', on_delete=models.CASCADE, blank=True, null=True)
    additional_image = models.ImageField(upload_to='people/images/additional_images/', blank=True)
    description = models.TextField(blank=True)

    def person_name(self):
        return self.linked_person.name

    def __str__(self):
        return f'Image for {self.linked_person.name}'
