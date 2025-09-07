from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import MindMap, MindMapNode
from .forms import MindMapForm, MindMapNodeForm

class MindMapListView(ListView):
    model = MindMap
    template_name = 'mindmaps/mindmap_index.html'
    context_object_name = 'mindmaps'

class MindMapDetailView(DetailView):
    model = MindMap
    template_name = 'mindmaps/mindmap_detail.html'
    context_object_name = 'mindmap'

class MindMapCreateView(CreateView):
    model = MindMap
    form_class = MindMapForm
    template_name = 'mindmaps/mindmap_form.html'
    success_url = reverse_lazy('mindmap_index')

class MindMapUpdateView(UpdateView):
    model = MindMap
    form_class = MindMapForm
    template_name = 'mindmaps/mindmap_form.html'
    success_url = reverse_lazy('mindmap_index')

class MindMapNodeCreateView(CreateView):
    model = MindMapNode
    form_class = MindMapNodeForm
    template_name = 'mindmaps/mindmapnode_form.html'
    success_url = reverse_lazy('mindmap_index')

class MindMapNodeUpdateView(UpdateView):
    model = MindMapNode
    form_class = MindMapNodeForm
    template_name = 'mindmaps/mindmapnode_form.html'
    success_url = reverse_lazy('mindmap_index')
