from django.http import Http404
from django.shortcuts import render
from django.db import connection as conn

# Create your views here.

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
    conn.cursor().execute("Select * FROM PENGGUNA")
    print(conn.cursor().fetchall)
    print()
    return render(request, "home.html", context)

def show_login(request):
    context = {}

    return render(request, "login.html", context)

def show_register(request):
    context = {}

    return render(request, "register.html", context)

def daftar_unduhan(request):
    context = {}

    return render(request, "daftar_unduhan.html", context)

def daftar_favorit(request):
    context = {}

    return render(request, "daftar_favorit.html", context)

def show_trailer(request):

    context = {
        'user': request.user,
    }

    return render(request, 'daftar_tayangan.html', context)

def show_tayangan(request, id_tayangan):
    tayangan_type = 'Unknown'
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM tayangan WHERE id = %s", [id_tayangan])
        tayangan = cursor.fetchone()
        cursor.execute("SELECT * FROM film WHERE id_tayangan = %s", [id_tayangan])
        film = cursor.fetchone()
        if film is not None:
            tayangan_type = 'Film'
        else:
            cursor.execute("SELECT * FROM series WHERE id_tayangan = %s", [id_tayangan])
            series = cursor.fetchone()
            if series is not None:
                tayangan_type = 'Series'

    if tayangan_type == 'Unknown':
        raise Http404("Tayangan does not exist")
    
    total_view = conn.cursor()
    if tayangan_type == 'Film':
        total_view.execute("""
            SELECT COUNT(*) as views
            FROM (
                SELECT 
                    id_tayangan, 
                    username, 
                    EXTRACT(EPOCH FROM (end_date_time - start_date_time)) / 60 as watch_duration
                FROM RIWAYAT_NONTON
                WHERE id_tayangan = %s
            ) as watch_sessions
            JOIN film ON film.id_tayangan = watch_sessions.id_tayangan
            WHERE watch_duration >= (film.durasi_film * 0.7)
            GROUP BY watch_sessions.id_tayangan
                        """, [id_tayangan])
        total_view = total_view.fetchone()
    # TODO Implement views for series
    # elif tayangan_type == 'Series':

    avg_rating = conn.cursor()
    avg_rating.execute("""
                SELECT AVG(rating) as avg_rating
                FROM ULASAN
                WHERE id_tayangan = %s
                    """, [id_tayangan])
    avg_rating = avg_rating.fetchone()

    genre = conn.cursor()
    genre.execute("""
                SELECT genre
                FROM GENRE_TAYANGAN
                WHERE id_tayangan = %s
                    """, [id_tayangan])
    genre = genre.fetchall()
    haveGenres = True
    if not genre:
        genre = "The genres have not been defined"
        haveGenres = False
    
    actors = conn.cursor()
    actors.execute("""
                SELECT nama
                FROM MEMAINKAN_TAYANGAN MT
                JOIN PEMAIN P on MT.id_pemain = P.id
                JOIN CONTRIBUTORS C on P.id = C.id
                WHERE id_tayangan = %s
                    """, [id_tayangan])
    actors = actors.fetchall()
    haveActors = True
    if not actors:
        actors = "The actors have not been defined"
        haveActors = False

    writers = conn.cursor()
    writers.execute("""
                SELECT nama
                FROM MENULIS_SKENARIO_TAYANGAN MST
                JOIN PENULIS_SKENARIO PS on MST.id_penulis_skenario = PS.id
                JOIN CONTRIBUTORS C on PS.id = C.id
                WHERE id_tayangan = %s
                    """, [id_tayangan])
    writers = writers.fetchall()
    haveWriters = True
    if not writers:
        writers = "The writers have not been defined"
        haveWriters = False

    sutradara = conn.cursor()
    sutradara.execute("""
                SELECT nama
                FROM SUTRADARA S
                JOIN CONTRIBUTORS C on S.id = C.id
                WHERE S.id = %s
                    """, [tayangan[7]])
    sutradara = sutradara.fetchone()
    if sutradara is None:
        sutradara = "The director has not been defined"
    else:
        sutradara = sutradara[0]
                      
    context = {
        'user': request.user,
        'tayangan_type': tayangan_type,
        'id': id_tayangan,
        'judul': tayangan[1],
        'sinopsis': tayangan[2],
        'asal_negara': tayangan[3],
        'sinopsis_trailer': tayangan[4],
        'url_video_trailer': tayangan[5],
        'release_date_trailer': tayangan[6],
        'id_sutradara': tayangan[7],
        'sutradara': sutradara,
        'total_view': total_view[0],
        'avg_rating': round(avg_rating[0], 2),
        'genre': genre,
        'haveGenres': haveGenres,
        'actors': actors,
        'haveActors': haveActors,
        'writers': writers,
        'haveWriters': haveWriters
    }

    if tayangan_type == 'Series':
        return show_series(request, context)
    elif tayangan_type == 'Film':
        context['url_video_film'] = film[1]
        context['release_date_film'] = film[2]
        context['durasi_film'] = film[3]
        return show_film(request, context)

def show_film(request, context):
    return render(request, 'halaman_film.html', context)

def show_series(request, context):
    return render(request, 'halaman_series.html', context)

def show_episode(request):
    
    context = {
        'user': request.user,
    }

    return render(request, 'halaman_episode.html', context)
