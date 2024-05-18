from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.db import connection as conn
from django.http import (HttpResponse, HttpResponseNotFound, HttpResponseRedirect,
                         JsonResponse)
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import psycopg2

# Create your views here.

def redir_homepage(request):
    return render(request, 'home.html')

def show_login(request, context=None):
    
    context={"logged_in": False}
    return render(request, 'login.html',context)

# @csrf_exempt
# def login(request):
    
#     if "username" in request.session:
#         context["logged_in"] = True
#         return redirect('main:show_home')
    

#     context = {
#         "logged_in": False
#     }
    
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')

#         #Search fom db
#         with conn.cursor() as query:
#             query.execute("set search_path to pacilflix")
#             query.execute(f"SELECT * FROM PENGGUNA WHERE username = '{username}' AND password = '{password}'")
#             pengguna = query.fetchone()
#             print(f"pengguna : {pengguna}")
            

#             #Wrong pass Redirect
#             if pengguna is None:
#                 context["message"] = "Username atau Password Salah"
#                 return render(request, 'login.html', context)
            
#             query.execute("set search_path to public")
#             request.session["username"] = username
#             request.session["logged_in"] = True
            
#             return redirect('main:show_home')
            
#     return render(request, 'login.html', context)

@csrf_exempt
def login(request):
    context = {"logged_in": False}

    if "username" in request.session:
        context["logged_in"] = True
        return redirect('main:show_home')

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Search from db
        try:
            with conn.cursor() as cursor:
                cursor.execute("SET search_path TO pacilflix")
                cursor.execute("SELECT * FROM PENGGUNA WHERE username = %s AND password = %s", (username, password))
                pengguna = cursor.fetchone()
                print(f"pengguna : {pengguna}")

                # Wrong pass Redirect
                if pengguna is None:
                    context["message"] = "Username atau Password Salah"
                    return render(request, 'login.html', context)

                cursor.execute("SET search_path TO public")
                request.session["username"] = username
                request.session["logged_in"] = True

                return redirect('main:show_home')
        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)
        finally:
            conn.close()

    return render(request, 'login.html', context)

def logout(request):
    request.session.flush()
    request.session.clear_expired()

    context = {
        "is_logged_in": False
    }
    return render(request, "home.html", context)

@csrf_exempt
def register_pengguna(request):
    context = {
        "logged_in": request.session.get("logged_in", False)
    }
    
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        negara_asal = request.POST.get('negara-asal')

        # Validate inputs
        if not username or not password or not negara_asal:
            context["message"] = "Semua field harus diisi."
            return render(request, 'register.html', context)
        
        with conn.cursor() as query:
            query.execute("SET search_path TO public")
            query.execute(f"SELECT * FROM PENGGUNA WHERE username = '{username}'")
            existing_user = query.fetchone()
            
            if existing_user:
                context["message"] = "Username sudah terdaftar, pilih username yang lain"
                return render(request, 'register.html', context)
            
            query.execute(f"INSERT INTO PENGGUNA (username, password, negara_asal) VALUES ('{username}', '{password}', '{negara_asal}')")
        
        # Automatically log the user in after registration
        request.session["username"] = username
        request.session["logged_in"] = True
        
        return redirect('main:show_home')
    
    return render(request, 'register.html', context)