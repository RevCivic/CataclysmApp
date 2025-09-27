from django.urls import path

from . import views

app_name = 'weapons'

urlpatterns = [
    path('', views.WeaponListView.as_view(), name='index'),
    path('add/', views.WeaponCreateView.as_view(), name='add'),
    path('<int:pk>/', views.WeaponDetailView.as_view(), name='detail'),
]