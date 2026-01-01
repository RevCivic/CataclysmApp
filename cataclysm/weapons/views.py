from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Weapon


class WeaponListView(ListView):
    model = Weapon
    template_name = "weapons/weapons.html"


class WeaponDetailView(DetailView):
    model = Weapon
    template_name = "weapons/detail.html"


class WeaponCreateView(CreateView):
    model = Weapon
    fields = "__all__"
    template_name = "weapons/add_object.html"

    def get_success_url(self):
        return reverse_lazy("weapons:detail", kwargs={"pk": self.object.pk})
