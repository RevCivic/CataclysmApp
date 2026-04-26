from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Event

_VALID_PER_PAGE = ('50', '100', '500', 'all')


class EventListView(ListView):
    model = Event
    template_name = 'events/events.html'
    context_object_name = 'object_list'

    def get_queryset(self):
        return Event.objects.all().order_by('name')

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


class EventCreateView(CreateView):
    model = Event
    # date is auto_now_add, exclude it; include all other user-editable fields
    fields = [
        'name', 'description', 'image', 'location',
        'people', 'factions', 'species', 'worlds', 'event_type', 'hidden',
    ]
    template_name = 'events/add_object.html'
    success_url = reverse_lazy('events:index')


class EventDetailView(DetailView):
    model = Event
    template_name = 'events/detail.html'
    context_object_name = 'object'

