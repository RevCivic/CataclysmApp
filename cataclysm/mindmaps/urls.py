from django.urls import path
from . import views

urlpatterns = [
    path('', views.MindMapListView.as_view(), name='mindmap_index'),
    path('add/', views.MindMapCreateView.as_view(), name='mindmap_add'),
    path('<int:pk>/', views.MindMapDetailView.as_view(), name='mindmap_detail'),
    path('<int:pk>/edit/', views.MindMapUpdateView.as_view(), name='mindmap_edit'),
    path('node/add/', views.MindMapNodeCreateView.as_view(), name='mindmapnode_add'),
    path('node/<int:pk>/edit/', views.MindMapNodeUpdateView.as_view(), name='mindmapnode_edit'),
]
