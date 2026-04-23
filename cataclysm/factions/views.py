from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Faction


class FactionListView(ListView):
    model = Faction
    template_name = 'factions/factions.html'
    context_object_name = 'object_list'
    paginate_by = 50

    def get_queryset(self):
        # prefetch M2M relations used by the list template (.count calls)
        return Faction.objects.prefetch_related('people', 'worlds', 'events').order_by('name')


class FactionCreateView(CreateView):
    model = Faction
    fields = '__all__'
    template_name = 'factions/add_object.html'
    success_url = reverse_lazy('factions:index')


class FactionDetailView(DetailView):
    model = Faction
    template_name = 'factions/detail.html'
    context_object_name = 'object'

