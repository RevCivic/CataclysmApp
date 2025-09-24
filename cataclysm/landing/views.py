from django.shortcuts import render


def landing_page(request):
    context = {}
    if request.user.is_authenticated:
        context['username'] = request.user.username
    return render(request, 'landing_page.html', context)
