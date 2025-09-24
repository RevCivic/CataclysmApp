from django.shortcuts import render



from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from .models import Party
from .forms import PartyForm


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


class PartyUpdateView(UpdateView):
	model = Party
	form_class = PartyForm
	template_name = 'party/party_form.html'
    
	def get_success_url(self):
		return reverse_lazy('party_page', kwargs={'pk': self.object.pk})

def add_party_images(request, pk):
	# Placeholder for add images logic
	return render(request, 'party/party.html', {})
