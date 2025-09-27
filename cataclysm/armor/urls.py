from django.urls import path

from . import views

app_name = 'armor'

urlpatterns = [
    path('', views.ArmorListView.as_view(), name='index'),
    path('add/', views.ArmorCreateView.as_view(), name='add'),
    path('<int:pk>/', views.ArmorDetailView.as_view(), name='detail'),
]