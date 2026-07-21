from django.urls import include, path

from . import views

urlpatterns = [
    path("", views.index, name="people_index"),
    path("index/", views.index, name="index"),
    path("add_person/", views.add_person, name="add_person"),
    path("export.csv", views.export_people_csv, name="export_people_csv"),
    path("views/save/", views.save_person_view, name="save_person_view"),
    path("views/<int:view_id>/", views.open_person_view, name="open_person_view"),
    path("<int:id>/", views.person_page, name="person_page"),
    path("edit_person/<int:id>", views.edit_person, name="edit_person"),
    path("delete_person/<int:id>", views.delete_person, name="delete_person"),
    path("add_images/<int:id>", views.add_images, name="add_images"),
]
