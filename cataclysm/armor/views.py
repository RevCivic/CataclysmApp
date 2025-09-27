from django.views import generic
from django.urls import reverse_lazy
from .models import Armor


class ArmorListView(generic.ListView):
    model = Armor
    template_name = 'armor/armor.html'
    context_object_name = 'object_list'


class ArmorDetailView(generic.DetailView):
    model = Armor
    template_name = 'armor/detail.html'


class ArmorCreateView(generic.CreateView):
    model = Armor
    fields = ['name', 'armor_type', 'base_armor_class', 'max_dexterity_bonus', 'armor_check_penalty', 'speed_penalty', 'weight', 'description', 'dynamic_tags', 'hidden']
    template_name = 'armor/add_object.html'
    success_url = reverse_lazy('armor:index')
from django.http import HttpResponse

index = make_index_view("armor")
