from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("import/", views.run_import, name="run_import"),
    path("read-sheet/", views.read_sheet, name="read_sheet"),
]