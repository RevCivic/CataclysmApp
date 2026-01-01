from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import Event


class EventListView(ListView):
    model = Event
    template_name = "events/events.html"


class EventDetailView(DetailView):
    model = Event
    template_name = "events/detail.html"


class EventCreateView(CreateView):
    model = Event
    fields = "__all__"
    template_name = "events/add_object.html"

    def get_success_url(self):
        return reverse_lazy("events:detail", kwargs={"pk": self.object.pk})
