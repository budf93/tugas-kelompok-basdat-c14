import json
from django.shortcuts import redirect, render
from django.db import connection
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from dateutil import parser
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from urllib.parse import unquote

# Create your views here.

#Untuk menyimpan data user login
def loggedin_user(request):
    return {
        'username': request.session.get('username', None),
        'error': request.session.get('error', False),
    }

def daftar_kontributor(request):
    context = {
    }

    return render(request, "daftar_kontributor.html", context)

def langganan(request):
    context = {
    }

    return render(request, "langganan.html", context)

def halaman_beli(request):
    context = {
    }

    return render(request, "halaman_beli.html", context)

def show_home(request):
    context = {}

    return render(request, "home.html", context)

def show_login(request):
    context = {}

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        login = connection.cursor()
        login.execute(f"""
            SELECT username, password, negara_asal
            FROM pacilflix.pengguna
            WHERE username = '{username}' AND password = '{password}';
        """)
        user = login.fetchall()
        print(user)
        if len(user) > 0:
            request.session['username'] = user[0][0] #PENTING BGT SETIAP LOGIN USERNAMENYA DISIMPEN DI SESSION
            return HttpResponseRedirect(reverse("main:show_tayangan"))

    return render(request, "login.html", context)

def show_register(request):
    context = {}

    return render(request, "register.html", context)

def daftar_unduhan(request):
    unduhan_user = connection.cursor()
    unduhan_user.execute(f"""
        SELECT t.judul, tt.timestamp
        FROM pacilflix.tayangan_terunduh as tt
        LEFT JOIN pacilflix.tayangan as t on tt.id_tayangan = t.id
        WHERE tt.username = '{request.session.get('username', None)}'; 
    """)

    context = {
        'daftar_unduhan': unduhan_user.fetchall(),
    }

    return render(request, "daftar_unduhan.html", context)

def delete_unduhan(request):
    if request.method == 'DELETE':
        judul = json.loads(request.body).get('judul')
        try:
            delete = connection.cursor()
            delete.execute(f"""
                DELETE FROM pacilflix.tayangan_terunduh
                WHERE id_tayangan IN (
                    SELECT id
                    FROM pacilflix.tayangan
                    WHERE judul = '{judul}'
                ) AND username = '{request.session.get('username', None)}';
                """)
            return HttpResponse(b"DELETED", 201)
        except Exception:
            request.session['error'] = "Tayangan minimal harus berada di daftar unduhan selama 1 hari agar bisa dihapus."
            return HttpResponseRedirect(reverse("main:daftar_unduhan"))
    
    return HttpResponseNotFound()

def tambah_unduhan(request):
    if request.method == 'POST':
        username = request.session.get('username', None)
        judul = request.POST.get('judul')
        cursor = connection.cursor()
        cursor.execute(f"""
            INSERT INTO pacilflix.tayangan_terunduh (id_tayangan, username, timestamp)
            SELECT t.id, '{username}', CURRENT_TIMESTAMP
            FROM pacilflix.tayangan t
            WHERE t.judul = '{judul}'
            AND NOT EXISTS (
                SELECT 1
                FROM pacilflix.tayangan_terunduh tt
                WHERE tt.id_tayangan = t.id
                AND tt.username = '{username}'
            );
        """)
        messages.success(request, f'Selamat! Anda telah berhasil mengunduh {judul} dan akan berlaku hingga [current time + 7 hari]. Cek informasi selengkapnya pada halaman daftar unduhan.')
        return HttpResponseRedirect(reverse('main:show_tayangan'))
    return HttpResponseNotFound()

@csrf_exempt
def clear_error(request):
    if request.method == 'POST':
        request.session['error'] = False  
        return redirect('main:daftar_unduhan')
    return HttpResponseNotAllowed(['POST'])

def daftar_favorit(request):
    favorit_user = connection.cursor()
    favorit_user.execute(f"""
        SELECT df.judul, df.timestamp
        FROM pacilflix.daftar_favorit as df
        WHERE df.username = '{request.session.get('username', None)}'; 
    """)

    context = {
        'daftar_favorit': favorit_user.fetchall(),
    }

    return render(request, "daftar_favorit.html", context)

def delete_daftar_favorit(request):
    if request.method == 'DELETE':
        judul = json.loads(request.body).get('judul')
        delete = connection.cursor()
        delete.execute(f"""
            DELETE FROM pacilflix.daftar_favorit
            WHERE judul = '{judul}' AND username = '{request.session.get('username', None)}';
        """)
        #"2023-12-15 22:03:55"
        return HttpResponse(b"DELETED", 201)
    
    return HttpResponseNotFound()

def isi_daftar_favorit(request, judul):
    judul = unquote(judul)
    favorite = connection.cursor()
    favorite.execute(f"""
        SELECT t.judul, df.judul as daftar_favorit, tdf.timestamp
        FROM pacilflix.daftar_favorit as df
        JOIN pacilflix.tayangan_memiliki_daftar_favorit as tdf
        ON df.username = tdf.username AND df.timestamp = tdf.timestamp
        LEFT JOIN pacilflix.tayangan as t
        ON t.id = tdf.id_tayangan
        WHERE df.username = '{request.session.get('username')}' AND df.judul = '{judul}';
    """)

    context = {
        'judul': judul,
        'favorites': favorite.fetchall(),
    }

    return render(request, "isi_daftar_favorit.html", context)

def delete_dari_favorit(request):
    if request.method == 'DELETE':
        nama_playlist = json.loads(request.body).get('nama')
        judul = json.loads(request.body).get('judul')
        delete = connection.cursor()
        delete.execute(f"""
            DELETE FROM pacilflix.tayangan_memiliki_daftar_favorit AS tdf
            USING pacilflix.daftar_favorit AS df, pacilflix.tayangan AS t
            WHERE tdf.username = df.username AND tdf.timestamp = df.timestamp
            AND t.id = tdf.id_tayangan
            AND df.username = '{request.session.get('username')}'
            AND t.judul = '{judul}'
            AND df.judul = '{nama_playlist}';
        """)
        return HttpResponse(b"DELETED", 201)
    
    return HttpResponseNotFound()

def add_to_favorit(request):
    if request.method == 'POST':
        judul = request.POST.get('judul_tayangan')
        daftar_favorit = request.POST.get('daftar_favorit')
        print(judul)
        print(daftar_favorit)
        cursor = connection.cursor()
        cursor.execute(f"""
            INSERT INTO pacilflix.TAYANGAN_MEMILIKI_DAFTAR_FAVORIT (id_tayangan, timestamp, username)
            SELECT 
                (SELECT t.id
                FROM pacilflix.tayangan AS t
                WHERE t.judul = '{judul}'),
                (SELECT df.timestamp
                FROM pacilflix.daftar_favorit AS df
                WHERE df.judul = '{daftar_favorit}'),
                '{request.session.get('username')}';
        """)
        return show_tayangan(request)
    
    return HttpResponseNotFound()

def show_trailer(request):

    context = {
        'user': request.user,
    }

    return render(request, 'daftar_tayangan.html', context)

def show_tayangan(request):
    cursor1 = connection.cursor()
    cursor1.execute(f"""
        SELECT judul, sinopsis, asal_negara, id
        FROM pacilflix.tayangan
        WHERE id = '2a4cc115-8f94-4e8b-bf77-d3380c9bf397';
    """)

    cursor2 = connection.cursor()
    cursor2.execute(f"""
        SELECT df.judul
        FROM pacilflix.daftar_favorit as df
        WHERE df.username = '{request.session.get('username', None)}';
    """)

    context = {
        'user': request.user,
        'tayangan': cursor1.fetchall(),
        'daftar_favorit': cursor2.fetchall(),
    }
    
    return render(request, 'halaman_tayangan.html', context)

def show_episode(request):
    
    context = {
        'user': request.user,
    }

    return render(request, 'halaman_episode.html', context)