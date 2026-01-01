from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import World


class WorldListView(ListView):
    model = World
    template_name = "worlds/worlds.html"


class WorldDetailView(DetailView):
    model = World
    template_name = "worlds/detail.html"


class WorldCreateView(CreateView):
    model = World
    fields = "__all__"
    template_name = "worlds/add_object.html"

    def get_success_url(self):
        return reverse_lazy("worlds:detail", kwargs={"pk": self.object.pk})
