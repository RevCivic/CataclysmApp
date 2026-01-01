from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Faction


class FactionListView(ListView):
    model = Faction
    template_name = "factions/factions.html"


class FactionDetailView(DetailView):
    model = Faction
    template_name = "factions/detail.html"


class FactionCreateView(CreateView):
    model = Faction
    fields = "__all__"
    template_name = "factions/add_object.html"

    def get_success_url(self):
        return reverse_lazy("factions:detail", kwargs={"pk": self.object.pk})
