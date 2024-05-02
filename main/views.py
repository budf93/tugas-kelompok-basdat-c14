from django.shortcuts import render

# Create your views here.

def show_home(request):
    context = {}

    return render(request, "home.html", context)

def show_login(request):
    context = {}

    return render(request, "login.html", context)

def show_register(request):
    context = {}

    return render(request, "register.html", context)

def show_trailer(request):

    context = {
        'user': request.user,
    }

    return render(request, 'daftar_tayangan.html', context)

def show_tayangan(request):
    
    context = {
        'user': request.user,
    }

    return render(request, 'halaman_tayangan.html', context)

def show_episode(request):
    
    context = {
        'user': request.user,
    }

    return render(request, 'halaman_episode.html', context)
def daftar_unduhan(request):
    context = {}

    return render(request, "daftar_unduhan.html", context)

def daftar_favorit(request):
    context = {}

    return render(request, "daftar_favorit.html", context)

