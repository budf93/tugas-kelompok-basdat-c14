import datetime
import json
from django.shortcuts import redirect, render
from django.db import connection
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseNotFound, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from dateutil import parser
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages
from urllib.parse import unquote
from django.views.decorators.http import require_http_methods
from django.db import connection as conn
import psycopg2


# Create your views here.

#Untuk menyimpan data user login
def loggedin_user(request):
    return {
        'username': request.session.get('username', None),
        'error': request.session.get('error', False),
    }

def daftar_kontributor(request):
    context = {
        "kontributor_list": [],
        "error": None}
    try:
        cursor = conn.cursor()
        query = """
        SELECT 
            nama, 
            string_agg(tipe, ', ') AS tipe, 
            jenis_kelamin, 
            kewarganegaraan
        FROM (
            SELECT 
                c.nama, 
                'Penulis Skenario' AS tipe, 
                c.jenis_kelamin, 
                c.kewarganegaraan
            FROM 
                contributors c
            JOIN 
                penulis_skenario ps ON c.id = ps.id
            UNION
            SELECT 
                c.nama, 
                'Pemain' AS tipe, 
                c.jenis_kelamin, 
                c.kewarganegaraan
            FROM 
                contributors c
            JOIN 
                pemain p ON c.id = p.id
            UNION
            SELECT 
                c.nama, 
                'Sutradara' AS tipe, 
                c.jenis_kelamin, 
                c.kewarganegaraan
            FROM 
                contributors c
            JOIN 
                sutradara s ON c.id = s.id
        ) AS combined
        GROUP BY 
            nama, 
            jenis_kelamin, 
            kewarganegaraan;
        """

        cursor.execute(query)
        kontributor_output = cursor.fetchall()

        context = {
        'kontributor_list' : [{
            "nama": res[0],
            "tipe": res[1],
            "jenis_kelamin": f'{"Laki-laki" if res[2] == 0 else "Perempuan"}',
            "kewarganegaraan": res[3]
        }
        for res in kontributor_output],
        }

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)
        context["error"] = "Error while fetching data from PostgreSQL"

    finally:
        # closing database connection.
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals() and conn:
            conn.close()
            print("PostgreSQL connection is closed")

    return render(request, "daftar_kontributor.html", context)


@require_http_methods(["GET","POST"])
def langganan(request):
    context = {}
    try:
        cursor = conn.cursor()
        # print(request.session.get('username'))
        #todo
        query = f"""SELECT distinct
            paket.nama, 
            paket.harga, 
            paket.resolusi_layar, 
            dukungan_perangkat.dukungan_perangkat AS dukungan_perangkat, 
            transaction.start_date_time, 
            transaction.end_date_time
        FROM 
            paket
        JOIN 
            dukungan_perangkat 
        ON 
            paket.nama = dukungan_perangkat.nama_paket
        JOIN 
            transaction 
        ON 
            paket.nama = transaction.nama_paket
        JOIN 
            pengguna 
        ON 
            transaction.username = '{request.session.get('username')}'
        WHERE
            transaction.end_date_time > NOW();"""

        cursor.execute(query)
        paket_langganan_output = cursor.fetchall()

        #todo
        query = """
            SELECT paket.nama, harga, resolusi_layar, string_agg(dukungan_perangkat, ', ')
            FROM paket        
            JOIN dukungan_perangkat ON paket.nama = dukungan_perangkat.nama_paket
            GROUP BY paket.nama, harga, resolusi_layar;
        """

        cursor.execute(query)
        paket_lain_output = cursor.fetchall()

        list_paket_lain = []

        for res in paket_lain_output:
            list_paket_lain.append({  
                "nama" : res[0],
                "harga" : res[1],
                "resolusi_layar": res[2],
                "dukungan_perangkat": res[3]
            })
        
        #todo
        query = f"""
        select 
        nama, transaction.start_date_time, transaction.end_date_time, metode_pembayaran, timestamp_pembayaran, harga
        from paket 
        join transaction on paket.nama = transaction.nama_paket
        join pengguna on pengguna.username = '{request.session.get('username')}'
        group by nama, transaction.start_date_time, transaction.end_date_time, metode_pembayaran, timestamp_pembayaran;
        """

        cursor.execute(query)
        riwayat_transaksi_output = cursor.fetchall()

        # list_riwayat_transaksi = []

        # for res in riwayat_transaksi_output:
        #     list_riwayat_transaksi.append({     
        #         "nama_paket": res[0],
        #         "tanggal_dimulai": res[1],
        #         "tanggal_akhir": res[2],
        #         "metode_pembayaran": res[3],
        #         "tanggal_pembayaran": res[4],
        #         "total_pembayaran" : res[5]
        #     })

        # cursor.execute(query)

        context = {
        'list_paket_langganan_aktif' : [{
            "nama" : res[0],
            "harga" : res[1],
            "resolusi_layar" : res[2],
            "dukungan_perangkat" : res[3],
            "tanggal_dimulai" : res[4],
            "tanggal_akhir" : res[5]
        }
        for res in paket_langganan_output],
        'list_paket_lain' : [{
            "nama" : res[0],
            "harga" : res[1],
            "resolusi_layar": res[2],
            "dukungan_perangkat": res[3]
        }
        for res in paket_lain_output],
        'list_riwayat_transaksi' : [{
            "nama_paket": res[0],
            "tanggal_dimulai": res[1],
            "tanggal_akhir": res[2],
            "metode_pembayaran": res[3],
            "tanggal_pembayaran": res[4],
            "total_pembayaran" : res[5]
        }
        for res in riwayat_transaksi_output],
        }
        
        # print(context)
        # return render(request, "langganan.html", context)

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")

    return render(request, "langganan.html", context)
            

@require_http_methods(["GET","POST"])
def halaman_beli(request, paket):
    paket_lain = []
    if request.session.get('username') is not None:
        try:          
            if request.method == "GET":
                nama = request.GET.get('nama')
                # print(nama)
            cursor = conn.cursor()
            if request.method == "POST":
                package_name = paket
                start_date = datetime.now()
                end_date = start_date + datetime.timedelta(days=30)
                payment_method = request.POST['payment_method']
                connection = conn.get_db_connection()
                cursor = conn.cursor()
                cursor.execute(
                    f"""select * from transaction where username = {request.session.get('username')}
                    and end_date_time > '{datetime.now.strftime("%Y-%m-%d %H:%M:%S")}'
                    """
                )
                langganan_aktif = cursor.fetchall() 
                if len(langganan_aktif) == 0:
                    cursor.execute(f"""
                        insert into transaction(username, nama_paket, start_date_time, end_date_time, metode_pembayaran, timestamp_pembayaran) 
                        values ('{request.session.get('username')}', '{package_name}', '{start_date.strftime("%Y-%m-%d %H:%M:%S")}', 
                        '{end_date.strftime("%Y-%m-%d %H:%M:%S")}', '{payment_method}', '{datetime.now.strftime("%Y-%m-%d %H:%M:%S")}')
                    """)
                else:
                    cursor.execute(
                    f"""
                    update transaction
                    set end_date_time = '{end_date.strftime("%Y-%m-%d %H:%M:%S")}'
                    metode_pembayaran = '{payment_method}'
                    timestamp_pembayaran = '{datetime.now.strftime("%Y-%m-%d %H:%M:%S")}'
                    nama_paket = '{package_name}'
                    where username='{request.session.get('username')}'
                    and end_date_time > '{datetime.now.strftime("%Y-%m-%d %H:%M:%S")}'
                    """
                    ) 
            else:
                # print(paket)
                cursor.execute(
                    f"""
                    select p.nama, p.harga, p.resolusi_layar, string_agg(dukungan_perangkat, ', ') as perangkat
                    from paket p join dukungan_perangkat d on p.nama=d.nama_paket
                    where p.nama='{paket}'
                    group by p.nama, p.harga, p.resolusi_layar
                    """
                )
                daftar_paket = cursor.fetchall()
                paket_lain = [
                {
                    "nama" : res[0],
                    "harga" : res[1],
                    "resolusi_layar" : res[2],
                    "dukungan_perangkat" : res[3],
                }
                for res in daftar_paket]
                
                # print(paket_lain[0]['resolusi_layar'])
                print(paket_lain)
                return render(request, 'halaman_beli.html', {'paket_lain':paket_lain})
            conn.commit()

        except (Exception, psycopg2.Error) as error:
            print("Error while fetching data from PostgreSQL", error)

        finally:
            # closing database connection.
            if conn:
                cursor.close()
                conn.close()
                print("PostgreSQL connection is closed")
    else:
        print(redirect('main:show_login'))

    return render(request, 'langganan.html', {'paket_lain':paket_lain[0]})

def show_home(request,context=None):
    print(context)
    if context is None:
        context = {
        "logged_in": False
    }
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