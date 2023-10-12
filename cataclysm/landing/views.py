from django.shortcuts import render

def landing_page(request):
    if request.user.is_authenticated:
        username = request.user.username
        return render(request, 'landing_page.html', {'username': username})
    else:
        return render(request, 'landing_page.html')