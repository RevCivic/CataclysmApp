from django.contrib import admin
from .models import Person, Statset, Skillset
# Register your models here.
admin.site.register(Person)
admin.site.register(Statset)
admin.site.register(Skillset)