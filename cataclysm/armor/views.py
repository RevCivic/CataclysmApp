from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Armor


class ArmorListView(ListView):
    model = Armor
    template_name = 'armor/armor.html'
    context_object_name = 'object_list'
    paginate_by = 50

    def get_queryset(self):
        return Armor.objects.all().order_by('name')


class ArmorCreateView(CreateView):
    model = Armor
    fields = '__all__'
    template_name = 'armor/add_object.html'
    success_url = reverse_lazy('armor:index')


class ArmorDetailView(DetailView):
    model = Armor
    template_name = 'armor/detail.html'
    context_object_name = 'object'

