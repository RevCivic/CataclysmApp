from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Armor

_VALID_PER_PAGE = ('50', '100', '500', 'all')


class ArmorListView(ListView):
    model = Armor
    template_name = 'armor/armor.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return Armor.objects.all().order_by('name')

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


class ArmorCreateView(CreateView):
    model = Armor
    fields = '__all__'
    template_name = 'armor/add_object.html'
    success_url = reverse_lazy('armor:index')


class ArmorDetailView(DetailView):
    model = Armor
    template_name = 'armor/detail.html'
    context_object_name = 'object'

