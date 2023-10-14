from django.urls import path
from people import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:id>", views.person_page, name="person_page"),
    path("add_person", views.add_person, name="add_person"),
    path("edit/<int:id>", views.edit_person, name="edit_person"),
]