from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from cataclysm.view_helpers import AddTagsFromInputMixin, PerPageMixin, SearchMixin, TagFilterMixin

from .models import Faction


class FactionListView(SearchMixin, TagFilterMixin, PerPageMixin, ListView):
    search_fields = ['name', 'description']
    model = Faction
    queryset = Faction.objects.prefetch_related('people', 'worlds', 'events', 'tags').order_by('name')
    template_name = 'factions/factions.html'
    context_object_name = 'object_list'


class FactionCreateView(AddTagsFromInputMixin, CreateView):
    model = Faction
    fields = '__all__'
    template_name = 'factions/add_object.html'
    success_url = reverse_lazy('factions:index')


class FactionDetailView(DetailView):
    model = Faction
    template_name = 'factions/detail.html'
    context_object_name = 'object'
