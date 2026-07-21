from django.contrib import admin
from .models import (
    AccommodationAssignment,
    Capability,
    OrganizationUnit,
    Person,
    PersonAlias,
    PersonAssignment,
    PersonCapability,
    PersonImage,
    PersonProfileFact,
    PersonRelationship,
    Skillset,
    Statset,
    Trait,
)

# Register your models here.
admin.site.register(Person)
admin.site.register(Statset)
admin.site.register(Skillset)
admin.site.register(PersonImage)
admin.site.register(Trait)
admin.site.register(PersonAlias)
admin.site.register(Capability)
admin.site.register(PersonCapability)
admin.site.register(OrganizationUnit)
admin.site.register(PersonAssignment)
admin.site.register(PersonRelationship)
admin.site.register(AccommodationAssignment)
admin.site.register(PersonProfileFact)
