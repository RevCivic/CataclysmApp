from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from people.models import Person
from .forms import PartyForm
from .models import Party


class PartyListView(ListView):
    model = Party
    template_name = 'party/party_index.html'
    context_object_name = 'party_list'
    paginate_by = 25

    def get_queryset(self):
        qs = Party.objects.prefetch_related('members').order_by('name')
        order_by = self.request.GET.get('order_by')
        if order_by:
            qs = qs.order_by(order_by)
        return qs


class PartyDetailView(DetailView):
    model = Party
    template_name = 'party/party.html'
    context_object_name = 'current_party'

    def get_queryset(self):
        return Party.objects.prefetch_related('members')


class PartyCreateView(CreateView):
    model = Party
    form_class = PartyForm
    template_name = 'party/party_form.html'

    def get_success_url(self):
        return reverse_lazy('party_page', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['people_list'] = Person.objects.all().order_by('name')
        context['selected_member_ids'] = set()
        return context


class PartyUpdateView(UpdateView):
    model = Party
    form_class = PartyForm
    template_name = 'party/party_form.html'

    def get_success_url(self):
        return reverse_lazy('party_page', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['people_list'] = Person.objects.all().order_by('name')
        context['selected_member_ids'] = set(
            self.object.members.values_list('pk', flat=True)
        )
        return context


def add_party_images(request, pk):
    # Images for Party are not yet modelled; redirect to the party detail.
    get_object_or_404(Party, pk=pk)
    return redirect('party_page', pk=pk)

