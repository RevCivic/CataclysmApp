from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Weapon


class WeaponListView(ListView):
    model = Weapon
    template_name = 'weapons/weapons.html'
    context_object_name = 'object_list'
    paginate_by = 50

    def get_queryset(self):
        return Weapon.objects.all().order_by('name')


class WeaponCreateView(CreateView):
    model = Weapon
    fields = '__all__'
    template_name = 'weapons/add_object.html'
    success_url = reverse_lazy('weapons:index')


class WeaponDetailView(DetailView):
    model = Weapon
    template_name = 'weapons/detail.html'
    context_object_name = 'object'

