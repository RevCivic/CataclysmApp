from django.contrib import admin
from .models import Species, Tag

# Register your models here.
admin.site.register(Species)
admin.site.register(Tag)