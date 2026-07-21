from django.conf import settings
from django.db import models


class Trait(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


# Create your models here.
class Person(models.Model):
    name = models.CharField(max_length=50)
    external_id = models.CharField(max_length=100, unique=True, null=True, blank=True)
    age = models.IntegerField(null=True, blank=True)
    age_text = models.CharField(max_length=50, blank=True)
    sex = models.CharField(max_length=50, default='None')
    species = models.ForeignKey('species.Species', on_delete=models.CASCADE, blank=True, null=True)
    faction = models.ForeignKey('factions.Faction', on_delete=models.SET_NULL, blank=True, null=True)
    rank = models.CharField(max_length=50, blank=True)
    position = models.CharField(max_length=50, blank=True)
    weapons = models.ManyToManyField('weapons.Weapon', blank=True)
    armors = models.ManyToManyField('armor.Armor', blank=True)
    bio = models.TextField(blank=True)
    image = models.ImageField(upload_to='people/images/', blank=True)
    image_source_url = models.URLField(blank=True, default='')
    stats = models.ForeignKey('Statset', on_delete=models.SET_NULL, blank=True, null=True)
    skills = models.ForeignKey('Skillset', on_delete=models.SET_NULL, blank=True, null=True)
    traits = models.ManyToManyField('Trait', blank=True)
    tags = models.ManyToManyField('tags.Tag', blank=True)
    location = models.CharField(max_length=50, blank=True)
    additional_images = models.ManyToManyField('PersonImage', blank=True)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class PersonAlias(models.Model):
    class Kind(models.TextChoices):
        ALIAS = 'alias', 'Alias'
        HERO = 'hero', 'Hero identity'
        NICKNAME = 'nickname', 'Nickname'
        FORMER = 'former', 'Former name'

    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='aliases')
    name = models.CharField(max_length=100)
    normalized_name = models.CharField(max_length=100, db_index=True, editable=False)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.ALIAS)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('person', 'normalized_name', 'kind'), name='unique_person_alias'),
        ]

    def save(self, *args, **kwargs):
        self.normalized_name = ' '.join(self.name.casefold().split())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Capability(models.Model):
    name = models.CharField(max_length=100)
    normalized_name = models.CharField(max_length=100, unique=True, editable=False)
    category = models.CharField(max_length=50, blank=True, db_index=True)

    def save(self, *args, **kwargs):
        self.normalized_name = ' '.join(self.name.casefold().split())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PersonCapability(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='capabilities')
    capability = models.ForeignKey(Capability, on_delete=models.CASCADE, related_name='people')
    raw_marker = models.CharField(max_length=20, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('person', 'capability'), name='unique_person_capability'),
        ]

    def __str__(self):
        return f'{self.person}: {self.capability}'


class OrganizationUnit(models.Model):
    class Kind(models.TextChoices):
        SHIP = 'ship', 'Ship'
        BRANCH = 'branch', 'Branch'
        DEPARTMENT = 'department', 'Department'
        TEAM = 'team', 'Team'
        CLAN = 'clan', 'Clan'
        OTHER = 'other', 'Other'

    name = models.CharField(max_length=100)
    normalized_name = models.CharField(max_length=100, editable=False)
    kind = models.CharField(max_length=16, choices=Kind.choices, default=Kind.OTHER)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, related_name='children', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('normalized_name', 'kind'), name='unique_organization_unit'),
        ]
        indexes = [models.Index(fields=('kind', 'normalized_name'))]

    def save(self, *args, **kwargs):
        self.normalized_name = ' '.join(self.name.casefold().split())
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class PersonAssignment(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='assignments')
    unit = models.ForeignKey(OrganizationUnit, on_delete=models.CASCADE, related_name='assignments')
    role = models.CharField(max_length=100, blank=True)
    rank = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=50, blank=True, db_index=True)
    is_primary = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('person', 'unit', 'role'), name='unique_person_unit_role'),
        ]
        indexes = [models.Index(fields=('unit', 'rank', 'role'))]

    def __str__(self):
        return f'{self.person} — {self.unit}'


class PersonRelationship(models.Model):
    from_person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='outgoing_relationships')
    to_person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        related_name='incoming_relationships',
        null=True,
        blank=True,
    )
    unresolved_name = models.CharField(max_length=100, blank=True)
    relationship_type = models.CharField(max_length=50, db_index=True)
    family_name = models.CharField(max_length=100, blank=True, db_index=True)
    notes = models.TextField(blank=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                check=(
                    models.Q(to_person__isnull=False, unresolved_name='')
                    | models.Q(to_person__isnull=True) & ~models.Q(unresolved_name='')
                ),
                name='relationship_resolved_or_named',
            ),
        ]

    def __str__(self):
        target = self.to_person or self.unresolved_name
        return f'{self.from_person} — {self.relationship_type} — {target}'


class AccommodationAssignment(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='accommodations')
    room = models.CharField(max_length=50, blank=True)
    section = models.CharField(max_length=50, blank=True, db_index=True)
    direction = models.CharField(max_length=50, blank=True)
    room_type = models.CharField(max_length=50, blank=True)
    is_current = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('person', 'room', 'section', 'direction'),
                name='unique_person_accommodation',
            ),
        ]

    def __str__(self):
        return f'{self.person}: {self.room or self.section}'


class PersonProfileFact(models.Model):
    person = models.ForeignKey(Person, on_delete=models.CASCADE, related_name='profile_facts')
    key = models.CharField(max_length=50)
    value = models.TextField(blank=True)
    normalized_value = models.CharField(max_length=255, blank=True, db_index=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('person', 'key'), name='unique_person_profile_fact'),
        ]
        indexes = [models.Index(fields=('key', 'normalized_value'))]

    def __str__(self):
        return f'{self.person}: {self.key}'


class SavedPersonView(models.Model):
    class Visibility(models.TextChoices):
        PRIVATE = 'private', 'Private'
        SHARED = 'shared', 'Shared'

    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='saved_person_views')
    name = models.CharField(max_length=100)
    visibility = models.CharField(max_length=10, choices=Visibility.choices, default=Visibility.PRIVATE)
    filters = models.JSONField(default=dict)
    columns = models.JSONField(default=list, blank=True)
    schema_version = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=('owner', 'name'), name='unique_saved_person_view_name'),
        ]
        ordering = ('name',)

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
