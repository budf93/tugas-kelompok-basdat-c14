from django.shortcuts import render

# Create your views here.
def show_main(request):
    context = {
    }

    return render(request, "main.html", context)

def daftar_kontributor(request):
    context = {
    }

    return render(request, "daftar_kontributor.html", context)

def langganan(request):
    context = {
    }

    return render(request, "langganan.html", context)