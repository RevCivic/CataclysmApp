from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic import CreateView, DetailView, ListView, UpdateView

from .forms import PartyForm
from .models import Party


class PartyListView(ListView):
    model = Party
    template_name = 'party/party_index.html'
    context_object_name = 'party_list'

    def get_queryset(self):
        qs = super().get_queryset()
        order_by = self.request.GET.get('order_by')
        if order_by:
            qs = qs.order_by(order_by)
        return qs


class PartyDetailView(DetailView):
    model = Party
    template_name = 'party/party.html'
    context_object_name = 'current_party'


class PartyCreateView(CreateView):
    model = Party
    form_class = PartyForm
    template_name = 'party/party_form.html'

    def get_success_url(self):
        return reverse_lazy('party_page', kwargs={'pk': self.object.pk})

	def get_context_data(self, **kwargs):
		context = {**super().get_context_data(**kwargs)}
		Person = apps.get_model('people', 'Person')
		# pass all people to the template so the available list can be populated
		context['people_list'] = Person.objects.all().order_by('name')
		# selected member ids (empty for new instances)
		form = context.get('form')
		selected_ids = []
		if form is not None:
			instance = getattr(form, 'instance', None)
			if instance is not None and instance.pk:
				selected_ids = list(instance.members.values_list('pk', flat=True))
		context['selected_member_ids'] = selected_ids
		return context


class PartyUpdateView(UpdateView):
    model = Party
    form_class = PartyForm
    template_name = 'party/party_form.html'

    def get_success_url(self):
        return reverse_lazy('party_page', kwargs={'pk': self.object.pk})


def add_party_images(request, pk):
    # Placeholder for add images logic
    return render(request, 'party/party.html', {})
