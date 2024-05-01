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

