from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView

from .models import World


class WorldListView(ListView):
    model = World
    template_name = 'worlds/worlds.html'
    context_object_name = 'object_list'
    paginate_by = 50

    def get_queryset(self):
        return World.objects.all().order_by('name')


class WorldCreateView(CreateView):
    model = World
    fields = '__all__'
    template_name = 'worlds/add_object.html'
    success_url = reverse_lazy('worlds:index')


class WorldDetailView(DetailView):
    model = World
    template_name = 'worlds/detail.html'
    context_object_name = 'object'

