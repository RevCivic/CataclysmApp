from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('people/', views.people_tools, name='people_tools'),
    path('people/import/', views.run_import, name='run_import'),
    path('people/read-sheet/', views.read_sheet, name='read_sheet'),
    path('people/species-upload/', views.people_species_upload, name='people_species_upload'),
    path('species/', views.species_tools, name='species_tools'),
    path('species/upload/', views.species_upload, name='species_upload'),
    path('species/import/', views.species_import, name='species_import'),
    path('duplicates/', views.duplicates, name='duplicates'),
    path('duplicates/confirm/', views.duplicates_confirm, name='duplicates_confirm'),
    path('duplicates/delete/', views.duplicates_delete, name='duplicates_delete'),
]
