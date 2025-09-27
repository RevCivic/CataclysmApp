from django.urls import path

from . import views

app_name = 'factions'

urlpatterns = [
    path('', views.FactionListView.as_view(), name='index'),
    path('add/', views.FactionCreateView.as_view(), name='add'),
    path('<int:pk>/', views.FactionDetailView.as_view(), name='detail'),
]