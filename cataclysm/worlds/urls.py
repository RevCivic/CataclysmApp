from django.urls import path

from . import views

app_name = 'worlds'

urlpatterns = [
    path('', views.WorldListView.as_view(), name='index'),
    path('add/', views.WorldCreateView.as_view(), name='add'),
    path('<int:pk>/', views.WorldDetailView.as_view(), name='detail'),
]