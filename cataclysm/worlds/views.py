from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from cataclysm.view_helpers import PerPageMixin, SearchMixin, TagFilterMixin

from .models import World


class WorldListView(SearchMixin, TagFilterMixin, PerPageMixin, ListView):
    search_fields = ['name', 'system']
    model = World
    queryset = World.objects.prefetch_related('tags').order_by('name')
    template_name = 'worlds/worlds.html'
    context_object_name = 'object_list'


class WorldCreateView(CreateView):
    model = World
    fields = '__all__'
    template_name = 'worlds/add_object.html'
    success_url = reverse_lazy('worlds:index')


class WorldDetailView(DetailView):
    model = World
    template_name = 'worlds/detail.html'
    context_object_name = 'object'
