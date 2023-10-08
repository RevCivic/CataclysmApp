from django.db import models

# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=50)
    age = models.IntegerField()
    species = models.ForeignKey('species.Species', on_delete=models.CASCADE)
    faction = models.ForeignKey('factions.Faction', on_delete=models.CASCADE)
    weapons = models.ManyToManyField('weapons.Weapon', blank=True)
    armors = models.ManyToManyField('armor.Armor', blank=True) 
    bio = models.TextField()
    image = models.ImageField(upload_to='people', blank=True)
    stats = models.OneToOneField('Stats', on_delete=models.CASCADE)
    skills = models.OneToOneField('Skills', on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    
    class Stats(models.Model):
        strength = models.IntegerField()
        intelligence = models.IntegerField()
        charisma = models.IntegerField()
        dexterity = models.IntegerField()
        constitution = models.IntegerField()
        wisdom = models.IntegerField()

        def __str__(self):
            return f'Stats for {self.person.name}'

    class Skills(models.Model):
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
            return f'Skills for {self.person.name}'