from django.http import HttpResponse
from django.shortcuts import render
from people.models import Person
#from people.forms import PersonForm


def index(request):
    people_list = Person.objects.all()
    order_by = request.GET.get('order_by')
    if order_by:
        people_list = people_list.order_by(order_by)
    context = {
        'people_list': people_list,
        
    }
    
    return render(request, 'people_index.html', context)