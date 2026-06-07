from django.contrib import admin
from .models import Person, Statset, Skillset, PersonImage, Tag, Trait

# Register your models here.
admin.site.register(Person)
admin.site.register(Statset)
admin.site.register(Skillset)
admin.site.register(PersonImage)
admin.site.register(Tag)
admin.site.register(Trait)
