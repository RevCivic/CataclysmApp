from django.urls import path
from . import views

urlpatterns = [
    path('', views.PartyListView.as_view(), name='party_index'),
    path('<int:pk>/', views.PartyDetailView.as_view(), name='party_page'),
    path('add/', views.PartyCreateView.as_view(), name='add_party'),
    path('<int:pk>/edit/', views.PartyUpdateView.as_view(), name='edit_party'),
    path('<int:pk>/add_images/', views.add_party_images, name='add_party_images'),
]
