from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import connection as conn
from django.http import (HttpResponse, HttpResponseNotFound, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt

# Create your views here.


def randoFunk(request):
    context = {}
    #Im just testing Here
    with conn.cursor() as cursor:
        cursor.execute("SET search_path TO public")
        cursor.execute("SELECT * FROM PENGGUNA")
        
        # Check if there are any results before fetching
        if cursor.rowcount > 0:
            test = cursor.fetchone()
            print(test)
        else:
            print("No results found")

    return render(request, "home.html", context)