from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponseBadRequest
from django.utils import timezone
from django.http import Http404
from django.shortcuts import redirect, render
from django.db import connection as conn
from django.views.decorators.csrf import csrf_exempt

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

def show_home(request,context=None):
    print(context)
    if context is None:
        context = {
        "logged_in": False
    }
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

def compute_riwayat_nonton(request):
    if request.method == 'POST':
        start = int(request.POST.get('start'))
        end = int(request.POST.get('end'))
        if start >= end:
            return HttpResponseBadRequest('Invalid slider values: start must be less than end.')
        start_date_time = datetime.strptime(request.POST.get('startTime'), '%Y-%m-%d %H:%M:%S')
        username = "jbecker" # TODO CHANGE THIS
        
        id_tayangan = request.POST.get('id_tayangan')
        tayangan_type = 'Unknown'
        with conn.cursor() as cursor:
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
        
        with conn.cursor() as durasi:
            if tayangan_type == 'Film':
                durasi.execute("""
                                SELECT durasi_film from film
                                WHERE id_tayangan = %s
                                """, [id_tayangan])
                durasi = durasi.fetchone()
            # TODO Implement views for series
            # elif tayangan_type == 'Series':

        durasi_tayangan = durasi[0]
        print(durasi_tayangan)

        # Convert durasi_tayangan to seconds
        durasi_tayangan_seconds = durasi_tayangan * 60

        # Compute the duration watched
        duration_watched_seconds = ((end - start) / 100) * durasi_tayangan_seconds

        # Compute end_date_time
        end_date_time = start_date_time + timedelta(seconds=duration_watched_seconds)
        print(start_date_time, end_date_time)

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO RIWAYAT_NONTON (id_tayangan, username, start_date_time, end_date_time)
                VALUES (%s, %s, %s, %s)
            """, [id_tayangan, username, start_date_time, end_date_time])
            conn.commit()
        
        return JsonResponse({'status': 'success'})

def insert_ulasan(request):
    if request.method == 'POST':
        id_tayangan_post = request.POST['id_tayangan_post']
        rating = request.POST['rating']
        deskripsi = request.POST.get('review_text', '')  # Default to empty string if not provided
        username = request.user  # Get the username of the currently logged in user #TODO change this
        timestamp = timezone.now()  # Get the current time

        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO ULASAN (id_tayangan, username, timestamp, rating, deskripsi)
                VALUES (%s, %s, %s, %s, %s)
            """, [id_tayangan_post, username, timestamp, rating, deskripsi])
            conn.commit()
    return redirect('main:show_tayangan', id_tayangan=id_tayangan_post)

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
    
    with conn.cursor() as total_view:
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

    with conn.cursor() as avg_rating:
        avg_rating.execute("""
                    SELECT AVG(rating) as avg_rating
                    FROM ULASAN
                    WHERE id_tayangan = %s
                        """, [id_tayangan])
        avg_rating = avg_rating.fetchone()

    with conn.cursor() as genre:
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
    
    with conn.cursor() as actors:
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

    with conn.cursor() as writers:
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

    with conn.cursor() as sutradara:
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

    with conn.cursor() as ulasan:
        ulasan.execute("""
                    SELECT *
                    FROM ULASAN
                    WHERE id_tayangan = %s
                    ORDER BY timestamp DESC
                        """, [id_tayangan])
        ulasan = ulasan.fetchall()
        haveUlasan = True
        if not ulasan:
            ulasan = "There are no reviews for this show"
            haveUlasan = False

    context = {
        'user': request.user, # TODO Username
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
        'haveWriters': haveWriters,
        'ulasan': ulasan,
        'haveUlasan': haveUlasan,
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
