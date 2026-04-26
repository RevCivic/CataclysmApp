from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("import/", views.run_import, name="run_import"),
    path("read-sheet/", views.read_sheet, name="read_sheet"),
    path("duplicates/", views.duplicates, name="duplicates"),
    path("duplicates/confirm/", views.duplicates_confirm, name="duplicates_confirm"),
    path("duplicates/delete/", views.duplicates_delete, name="duplicates_delete"),
]
