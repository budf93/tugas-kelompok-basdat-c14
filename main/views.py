from datetime import datetime, timedelta, date
import math
from django.utils import timezone
from django.http import Http404
from django.shortcuts import redirect, render
from django.db import connection as conn
from django.views.decorators.csrf import csrf_exempt
from functools import wraps
import json
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseRedirect, JsonResponse, HttpResponseBadRequest
from django.urls import reverse
from dateutil import parser
from django.contrib import messages
from urllib.parse import unquote

# Create your views here.

def login_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if "username" in request.session:
            # User is logged in, proceed to the view
            return view_func(request, *args, **kwargs)
        else:
            # User is a guest, redirect to login page
            return redirect('authentication:login')
    return _wrapped_view

def check_package(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if check_active_package(request):
            return view_func(request, *args, **kwargs)
        else:
            return redirect('main:langganan')
    return _wrapped_view

def check_active_package(request):
    displayTombol = False
    if "username" in request.session:
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO extensions")
            now = datetime.now()

            query = """
                SELECT * FROM TRANSACTION
                WHERE username = %s AND start_date_time <= %s AND end_date_time >= %s
            """

            cursor.execute(query, (request.session["username"], now, now))

            result = cursor.fetchone()

            if result is not None:
                displayTombol = True

    return displayTombol

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
    with conn.cursor() as unduhan_user:
        unduhan_user.execute("SET search_path TO extensions")
        unduhan_user.execute(f"""
            SELECT t.judul, tt.timestamp
            FROM tayangan_terunduh as tt
            LEFT JOIN tayangan as t on tt.id_tayangan = t.id
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
            with conn.cursor() as delete:
                delete.execute("SET search_path TO extensions")
                delete.execute(f"""
                    DELETE FROM tayangan_terunduh
                    WHERE id_tayangan IN (
                        SELECT id
                        FROM tayangan
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
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO extensions")
            cursor.execute(f"""
                INSERT INTO tayangan_terunduh (id_tayangan, username, timestamp)
                SELECT t.id, '{username}', CURRENT_TIMESTAMP
                FROM tayangan t
                WHERE t.judul = '{judul}'
                AND NOT EXISTS (
                    SELECT 1
                    FROM tayangan_terunduh tt
                    WHERE tt.id_tayangan = t.id
                    AND tt.username = '{username}'
                );
            """)
        messages.success(request, f'Selamat! Anda telah berhasil mengunduh {judul} dan akan berlaku hingga [current time + 7 hari]. Cek informasi selengkapnya pada halaman daftar unduhan.')
        return HttpResponseRedirect(reverse('main:show_tayangan'))
    return HttpResponseNotFound()

def daftar_favorit(request):
    with conn.cursor() as favorit_user:
        favorit_user.execute("SET search_path TO extensions")
        favorit_user.execute(f"""
            SELECT df.judul, df.timestamp
            FROM daftar_favorit as df
            WHERE df.username = '{request.session.get('username', None)}'; 
        """)

    context = {
        'daftar_favorit': favorit_user.fetchall(),
    }

    return render(request, "daftar_favorit.html", context)

def delete_daftar_favorit(request):
    if request.method == 'DELETE':
        judul = json.loads(request.body).get('judul')
        with conn.cursor() as delete:
            delete.execute("SET search_path TO extensions")
            delete.execute(f"""
                DELETE FROM daftar_favorit
                WHERE judul = '{judul}' AND username = '{request.session.get('username', None)}';
            """)
        #"2023-12-15 22:03:55"
        return HttpResponse(b"DELETED", 201)
    
    return HttpResponseNotFound()

def isi_daftar_favorit(request, judul):
    judul = unquote(judul)
    with conn.cursor() as favorite:
        favorite.execute("SET search_path TO extensions")
        favorite.execute(f"""
            SELECT t.judul, df.judul as daftar_favorit, tdf.timestamp
            FROM daftar_favorit as df
            JOIN tayangan_memiliki_daftar_favorit as tdf
            ON df.username = tdf.username AND df.timestamp = tdf.timestamp
            LEFT JOIN tayangan as t
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
        with conn.cursor() as delete:
            delete.execute("SET search_path TO extensions")
            delete.execute(f"""
                DELETE FROM tayangan_memiliki_daftar_favorit AS tdf
                USING daftar_favorit AS df, tayangan AS t
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
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO extensions")
            cursor.execute(f"""
                INSERT INTO TAYANGAN_MEMILIKI_DAFTAR_FAVORIT (id_tayangan, timestamp, username)
                SELECT 
                    (SELECT t.id
                    FROM tayangan AS t
                    WHERE t.judul = '{judul}'),
                    (SELECT df.timestamp
                    FROM daftar_favorit AS df
                    WHERE df.judul = '{daftar_favorit}'),
                    '{request.session.get('username')}';
            """)
        return show_tayangan(request)
    
    return HttpResponseNotFound()

def search_tayangan(request):
    title = request.GET.get('title', '')
    
    if not title:
        return redirect('main:show_daftar_tayangan')
    
    with conn.cursor() as cursor:
        cursor.execute("SET search_path TO extensions")
        cursor.execute("SELECT id, judul, sinopsis_trailer, url_video_trailer, release_date_trailer FROM tayangan WHERE judul ILIKE %s", ['%' + title + '%'])
        shows = cursor.fetchall()

    displayTombol = check_active_package(request)

    context = {'shows': shows, 'displayTombol': displayTombol, 'title': title}

    return render(request, 'hasil_pencarian.html', context)

def show_daftar_tayangan(request):
    with conn.cursor() as cursor:
        cursor.execute("SET search_path TO extensions")

        # Query for top 10 shows of the week
        # Asumsi menggunakan start_date_time untuk menentukan jumlah viewsnya
        cursor.execute("""
            SELECT * FROM (
                (SELECT id_tayangan, judul, sinopsis_trailer, url_video_trailer, release_date_trailer, views 
                FROM (
                    SELECT watch_sessions.id_tayangan, COUNT(*) as views
                    FROM (
                        SELECT 
                            id_tayangan, 
                            username, 
                            EXTRACT(EPOCH FROM (end_date_time - start_date_time)) / 60 as watch_duration
                        FROM RIWAYAT_NONTON
                        WHERE start_date_time >= NOW() - INTERVAL '7 days'
                    ) as watch_sessions
                    JOIN film ON film.id_tayangan = watch_sessions.id_tayangan
                    WHERE watch_duration >= (film.durasi_film * 0.7)
                    GROUP BY watch_sessions.id_tayangan
                ) as tayangan_views
                JOIN tayangan on tayangan.id = tayangan_views.id_tayangan)
                UNION ALL
                (WITH durasi_series AS (
                    SELECT 
                        e.id_series,
                        AVG(e.durasi) AS avg_duration
                    FROM 
                        EPISODE e
                    GROUP BY 
                        e.id_series
                ),
                watch_sessions AS (
                    SELECT 
                        id_tayangan, 
                        username, 
                        EXTRACT(EPOCH FROM (end_date_time - start_date_time)) / 60 as watch_duration
                    FROM RIWAYAT_NONTON
                    WHERE start_date_time >= NOW() - INTERVAL '7 days'
                ),
                total_watch_session AS (
                    SELECT
                        watch_sessions.id_tayangan,
                        SUM(watch_sessions.watch_duration) as total_watch_duration
                    FROM
                        watch_sessions
                    GROUP BY
                        watch_sessions.id_tayangan
                )
                SELECT 
                    total_watch_session.id_tayangan, 
                    judul, 
                    sinopsis_trailer, 
                    url_video_trailer, 
                    release_date_trailer,
                    ceil(total_watch_session.total_watch_duration / durasi_series.avg_duration) as views
                FROM
                    total_watch_session
                JOIN
                    durasi_series
                ON
                    total_watch_session.id_tayangan = durasi_series.id_series
                JOIN 
                    tayangan
                ON 
                    tayangan.id = durasi_series.id_series)
            ) AS combined_results
            ORDER BY views DESC
            LIMIT 10
        """)
        top_shows = cursor.fetchall()

        # Query for all films
        cursor.execute("""
                    SELECT id, judul, sinopsis_trailer, url_video_trailer, 
                    release_date_trailer 
                    FROM film
                    JOIN tayangan on id = id_tayangan""")
        films = cursor.fetchall()

        # Query for all series
        cursor.execute("""
                    SELECT id, judul, sinopsis_trailer, url_video_trailer, 
                    release_date_trailer 
                    FROM series
                    JOIN tayangan on id = id_tayangan""")
        series = cursor.fetchall()

    displayTombol = check_active_package(request)
    
    # Pass the data to the template
    context = {'films': films, 'series': series, 'top_shows': top_shows, 'displayTombol': displayTombol}
    return render(request, 'daftar_tayangan.html', context)

@login_required
def compute_riwayat_nonton(request):
    if request.method == 'POST':
        start = int(request.POST.get('start'))
        end = int(request.POST.get('end'))
        if start >= end:
            return HttpResponseBadRequest('Invalid slider values: start must be less than end.')
        start_date_time = datetime.strptime(request.POST.get('startTime'), '%Y-%m-%d %H:%M:%S')
        username = request.session.get('username')
        
        id_tayangan = request.POST.get('id_tayangan')
        tayangan_type = 'Unknown'
        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO extensions")
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
            durasi.execute("SET search_path TO extensions")
            if tayangan_type == 'Film':
                durasi.execute("""
                                SELECT durasi_film from film
                                WHERE id_tayangan = %s
                                """, [id_tayangan])
            # TODO Implement views for series
            elif tayangan_type == 'Series':
                sub_judul = request.POST.get('sub_judul')
                durasi.execute("""
                                SELECT durasi from episode
                                WHERE id_series = %s AND sub_judul = %s
                                """, [id_tayangan, sub_judul])
            durasi = durasi.fetchone()

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
            cursor.execute("SET search_path TO extensions")
            cursor.execute("""
                INSERT INTO RIWAYAT_NONTON (id_tayangan, username, start_date_time, end_date_time)
                VALUES (%s, %s, %s, %s)
            """, [id_tayangan, username, start_date_time, end_date_time])
            conn.commit()
        
        return JsonResponse({'status': 'success'})

@login_required
def insert_ulasan(request):
    if request.method == 'POST':
        id_tayangan_post = request.POST['id_tayangan_post']
        rating = request.POST['rating']
        deskripsi = request.POST.get('review_text', '')  # Default to empty string if not provided
        username = request.session.get('username')
        timestamp = timezone.now()  # Get the current time

        with conn.cursor() as cursor:
            cursor.execute("SET search_path TO extensions")
            cursor.execute("""
                INSERT INTO ULASAN (id_tayangan, username, timestamp, rating, deskripsi)
                VALUES (%s, %s, %s, %s, %s)
            """, [id_tayangan_post, username, timestamp, rating, deskripsi])
            conn.commit()
    return redirect('main:show_tayangan', id_tayangan=id_tayangan_post)

# Asumsi page tayangan hanya bisa ditampilkan jika paket aktif
@login_required
@check_package
def show_tayangan(request, id_tayangan):
    tayangan_type = 'Unknown'
    with conn.cursor() as cursor:
        cursor.execute("SET search_path TO extensions")
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
        total_view.execute("SET search_path TO extensions")
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
        # Asumsi cara perhitungan total views adalah sbb:
        # 1. Menghitung average_duration dari seluruh episodes pada suatu series
        # 2. Menjumlahkan total_watch_duration dari suatu series
        # 3. Total view akan berupa total_watch_duration / average_duration
        elif tayangan_type == 'Series':
            total_view.execute("""
                WITH durasi_series AS (
                    SELECT 
                        e.id_series,
                        AVG(e.durasi) AS avg_duration
                    FROM 
                        EPISODE e
                    WHERE 
                        e.id_series = %s
                    GROUP BY 
                        e.id_series
                ),
                watch_sessions AS (
                    SELECT 
                        id_tayangan, 
                        username, 
                        EXTRACT(EPOCH FROM (end_date_time - start_date_time)) / 60 as watch_duration
                    FROM RIWAYAT_NONTON
                    WHERE id_tayangan = %s
                ),
                total_watch_session AS (
                    SELECT
                        watch_sessions.id_tayangan,
                        SUM(watch_sessions.watch_duration) as total_watch_duration
                    FROM
                        watch_sessions
                    WHERE
                        watch_sessions.id_tayangan = %s
                    GROUP BY
                        watch_sessions.id_tayangan
                )
                SELECT 
                    total_watch_session.total_watch_duration / durasi_series.avg_duration as views
                FROM
                    total_watch_session
                JOIN
                    durasi_series
                ON
                    total_watch_session.id_tayangan = durasi_series.id_series
                                    """, [id_tayangan, id_tayangan, id_tayangan])
            total_view = total_view.fetchone()

    with conn.cursor() as avg_rating:
        avg_rating.execute("SET search_path TO extensions")
        avg_rating.execute("""
                    SELECT AVG(rating) as avg_rating
                    FROM ULASAN
                    WHERE id_tayangan = %s
                        """, [id_tayangan])
        avg_rating = avg_rating.fetchone()

    with conn.cursor() as genre:
        genre.execute("SET search_path TO extensions")
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
        actors.execute("SET search_path TO extensions")
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
        writers.execute("SET search_path TO extensions")
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
        sutradara.execute("SET search_path TO extensions")
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
        ulasan.execute("SET search_path TO extensions")
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

    with conn.cursor() as cursor2:
        cursor2.execute("SET search_path TO extensions")
        cursor2.execute(f"""
            SELECT df.judul
            FROM daftar_favorit as df
            WHERE df.username = '{request.session.get('username', None)}';
        """)
        daftar_favorit = cursor2.fetchall()

    context = {
        'user': request.session.get('username'),
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
        'total_view': math.floor(total_view[0]) if total_view is not None else None,
        'avg_rating': round(avg_rating[0], 2) if avg_rating[0] is not None else None,
        'genre': genre,
        'haveGenres': haveGenres,
        'actors': actors,
        'haveActors': haveActors,
        'writers': writers,
        'haveWriters': haveWriters,
        'ulasan': ulasan,
        'haveUlasan': haveUlasan,
        'daftar_favorit': daftar_favorit,
        'tayangan': tayangan
    }

    if tayangan_type == 'Series':
        with conn.cursor() as episodes:
            episodes.execute("SET search_path TO extensions")
            episodes.execute("""
                        SELECT *
                        FROM EPISODE
                        WHERE id_series = %s
                        ORDER BY release_date asc
                            """, [id_tayangan])
            episodes = episodes.fetchall()
            haveEpisodes = True
            if not episodes:
                episodes = "There are no episodes for this series"
                haveEpisodes = False
            context['episodes'] = episodes
            context['haveEpisodes'] = haveEpisodes
        return show_series(request, context)
    elif tayangan_type == 'Film':
        context['url_video_film'] = film[1]
        context['release_date_film'] = film[2].strftime('%Y-%m-%d')
        context['durasi_film'] = film[3]
        return show_film(request, context)

@login_required
def show_film(request, context):
    return render(request, 'halaman_film.html', context)

@login_required
def show_series(request, context):
    return render(request, 'halaman_series.html', context)

@login_required
def show_episode(request, id_tayangan, judul, sub_judul):
    with conn.cursor() as episode:
        episode.execute("SET search_path TO extensions")
        episode.execute("""
                    SELECT *
                    FROM EPISODE
                    WHERE id_series = %s AND sub_judul = %s
                        """, [id_tayangan, sub_judul])
        episode = episode.fetchone()
    
    with conn.cursor() as other_episode:
        other_episode.execute("SET search_path TO extensions")
        other_episode.execute("""
                    SELECT *
                    FROM EPISODE
                    WHERE id_series = %s and sub_judul <> %s
                        """, [id_tayangan, sub_judul])
        other_episode = other_episode.fetchall()
        haveOtherEpisodes = True
        if not other_episode:
            other_episode = "There are no other episodes for this series"
            haveOtherEpisodes = False

    context = {
        'user': request.session.get('username'),
        'id': id_tayangan,
        'judul': judul,
        'sub_judul': sub_judul,
        'other_episode': other_episode,
        'haveOtherEpisodes': haveOtherEpisodes,
        'sinopsis_episode': episode[2],
        'url_episode': episode[4],
        'release_date_episode': episode[5].strftime('%Y-%m-%d'),
        'durasi': episode[3],
    }

    return render(request, 'halaman_episode.html', context)