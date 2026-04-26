from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Faction

_VALID_PER_PAGE = ('50', '100', '500', 'all')


class FactionListView(ListView):
    model = Faction
    template_name = 'factions/factions.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        # prefetch M2M relations used by the list template (.count calls)
        return Faction.objects.prefetch_related('people', 'worlds', 'events').order_by('name')

    def get_paginate_by(self, queryset):
        per_page = self.request.GET.get('per_page', '50')
        if per_page == 'all':
            return None
        if per_page in ('50', '100', '500'):
            return int(per_page)
        return 50

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        per_page = self.request.GET.get('per_page', '50')
        ctx['current_per_page'] = per_page if per_page in _VALID_PER_PAGE else '50'
        return ctx


class FactionCreateView(CreateView):
    model = Faction
    fields = '__all__'
    template_name = 'factions/add_object.html'
    success_url = reverse_lazy('factions:index')


class FactionDetailView(DetailView):
    model = Faction
    template_name = 'factions/detail.html'
    context_object_name = 'object'

