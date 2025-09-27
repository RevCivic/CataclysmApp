from django.urls import path

from . import views

app_name = 'events'

urlpatterns = [
    path('', views.EventListView.as_view(), name='index'),
    path('add/', views.EventCreateView.as_view(), name='add'),
    path('<int:pk>/', views.EventDetailView.as_view(), name='detail'),
]