from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Event


class EventListView(ListView):
    model = Event
    template_name = 'events/events.html'
    context_object_name = 'object_list'
    paginate_by = 50

    def get_queryset(self):
        return Event.objects.all().order_by('name')


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

