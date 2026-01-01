from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Armor


class ArmorListView(ListView):
    model = Armor
    template_name = "armor/armor.html"


class ArmorDetailView(DetailView):
    model = Armor
    template_name = "armor/detail.html"


class ArmorCreateView(CreateView):
    model = Armor
    fields = "__all__"
    template_name = "armor/add_object.html"

    def get_success_url(self):
        return reverse_lazy("armor:detail", kwargs={"pk": self.object.pk})
