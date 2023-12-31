from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("index/", views.index, name="index"),
    path("add/", views.add, name="add"),
    path("<int:id>/", views.species_page, name="species_page"),
    path("edit/<int:id>", views.edit_species, name="edit_species"),
]