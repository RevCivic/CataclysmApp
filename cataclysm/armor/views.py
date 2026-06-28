from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from cataclysm.view_helpers import PerPageMixin, SearchMixin, TagFilterMixin

from .models import Armor


class ArmorListView(SearchMixin, TagFilterMixin, PerPageMixin, ListView):
    search_fields = ['name', 'armor_type']
    model = Armor
    queryset = Armor.objects.prefetch_related('tags').order_by('name')
    template_name = 'armor/armor.html'
    context_object_name = 'object_list'


class ArmorCreateView(CreateView):
    model = Armor
    fields = '__all__'
    template_name = 'armor/add_object.html'
    success_url = reverse_lazy('armor:index')


class ArmorDetailView(DetailView):
    model = Armor
    template_name = 'armor/detail.html'
    context_object_name = 'object'
