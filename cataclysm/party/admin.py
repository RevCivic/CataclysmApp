from django.contrib import admin

from .models import Party

@admin.register(Party)
class PartyAdmin(admin.ModelAdmin):
	list_display = ("name", "type", "leader", "faction", "location", "hidden", "created_at", "updated_at")
	search_fields = ("name", "leader", "faction", "location")
	list_filter = ("type", "faction", "hidden")
