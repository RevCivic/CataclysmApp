from django.db import models
from django.utils import timezone

# Basic Party model for demonstration, to be expanded later
class Party(models.Model):
	name = models.CharField(
		max_length=100,
		verbose_name="Party Name",
		help_text="Enter the name of the party."
	)
	type = models.CharField(
		max_length=100,
		blank=True,
		null=True,
		verbose_name="Party Type",
		help_text="Type or category of the party (e.g., adventuring, political, etc.)."
	)
	leader = models.CharField(
		max_length=100,
		blank=True,
		null=True,
		verbose_name="Leader",
		help_text="Name of the party leader."
	)
	faction = models.CharField(
		max_length=100,
		blank=True,
		null=True,
		verbose_name="Faction",
		help_text="Faction this party is associated with."
	)
	location = models.CharField(
		max_length=100,
		blank=True,
		null=True,
		verbose_name="Location",
		help_text="Current location of the party."
	)
	purpose = models.TextField(
		blank=True,
		null=True,
		verbose_name="Purpose",
		help_text="Describe the purpose or mission of the party."
	)
	hidden = models.BooleanField(
		default=False,
		verbose_name="Hidden",
		help_text="Should this party be hidden from public view?"
	)
	created_at = models.DateTimeField(
		auto_now_add=True,
		verbose_name="Created At",
		help_text="The date and time this party was created."
	)
	updated_at = models.DateTimeField(
		auto_now=True,
		verbose_name="Updated At",
		help_text="The date and time this party was last updated."
	)
	# Add more fields as needed

	def __str__(self):
		return self.name
