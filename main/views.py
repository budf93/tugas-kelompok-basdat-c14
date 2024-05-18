from django.shortcuts import render, redirect
import psycopg2
from django.db import connection as conn
from django.views.decorators.http import require_http_methods

def daftar_kontributor(request):
    try:
        cursor = conn.cursor()
        query = """
        (
        SELECT 
            c.nama, 
            'Penulis Skenario' AS tipe, 
            c.jenis_kelamin, 
            c.kewarganegaraan
        FROM 
            contributors c
        JOIN 
            penulis_skenario ps ON c.id = ps.id
        )
        UNION
        (
        SELECT 
            c.nama, 
            'Pemain' AS tipe, 
            c.jenis_kelamin, 
            c.kewarganegaraan
        FROM 
            contributors c
        JOIN 
            pemain p ON c.id = p.id
        )
        UNION
        (
        SELECT 
            c.nama, 
            'Sutradara' AS tipe, 
            c.jenis_kelamin, 
            c.kewarganegaraan
        FROM 
            contributors c
        JOIN 
            sutradara s ON c.id = s.id;
        )
        """

        cursor.execute(query)
        kontributor_output = cursor.fetchall()

        kontributor_list = []

        for res in kontributor_output:
            kontributor_list.append({
                "id": res[0],
                "nama": res[1],
                "tipe": res[2],
                "jenis_kelamin": res[3],
                "kewarganegaraan": res[4]         
            })

        #send all data to html through context 
        context = {
            "kontributor_list" : kontributor_list,
        }

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")

    return render(request, "daftar_kontributor.html", context)


@require_http_methods(["GET","POST"])
def langganan(request):
    try:
        cursor = conn.cursor()

        print(request.session.get('username'))
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

        # #todo
        # query = """
        #     SELECT paket.nama, harga, resolusi_layar, string_agg(dukungan_perangkat, ', ')
        #     FROM paket        
        #     JOIN dukungan_perangkat ON paket.nama = dukungan_perangkat.nama_paket
        #     GROUP BY paket.nama, harga, resolusi_layar;
        # """

        # cursor.execute(query)
        # paket_lain_output = cursor.fetchall()

        # list_paket_lain = []

        # for res in paket_lain_output:
        #     list_paket_lain.append({  
        #         "nama" : res[0],
        #         "harga" : res[1],
        #         "resolusi_layar": res[2],
        #         "dukungan_perangkat": res[3]
        #     })
        
        # #todo
        # query = f"""
        # select 
        # nama, transaction.start_date_time, transaction.end_date_time, metode_pembayaran, timestamp_pembayaran, sum(harga)
        # from paket 
        # join transaction on paket.nama = transaction.nama_paket
        # join pengguna on transaction.username = {request.session.get('username')}
        # group by nama, transaction.start_date_time, transaction.end_date_time, metode_pembayaran, timestamp_pembayaran;
        # """

        # cursor.execute(query)
        # riwayat_transaksi_output = cursor.fetchall()

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

        # cursor.execute()

        # #send all data to html through context 
        # context = {
        #     'list_paket_langganan_aktif':list_paket_langganan_aktif,
        #     'list_paket_lain':list_paket_lain,
        #     'list_riwayat_transaksi':list_riwayat_transaksi
        # }

        # context = {
        #     'list_paket_langganan_aktif' : list_paket_langganan_aktif
        # }

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
        # 'list_paket_lain' : [{
        #     "nama" : res[0],
        #         "harga" : res[1],
        #         "resolusi_layar": res[2],
        #         "dukungan_perangkat": res[3]
        # }
        # for res in paket_lain_output],
        # 'list_riwayat_transaksi' : [{
        #     "nama_paket": res[0],
        #     "tanggal_dimulai": res[1],
        #     "tanggal_akhir": res[2],
        #     "metode_pembayaran": res[3],
        #     "tanggal_pembayaran": res[4],
        #     "total_pembayaran" : res[5]
        # }
        # for res in riwayat_transaksi_output],
        }
        return render(request, "langganan.html", context)

    except (Exception, psycopg2.Error) as error:
        print("Error while fetching data from PostgreSQL", error)

    finally:
        # closing database connection.
        if conn:
            cursor.close()
            conn.close()
            print("PostgreSQL connection is closed")
        
    # return redirect("main:halaman_beli")
            

@require_http_methods(["GET","POST"])
def halaman_beli(request):
    if request.session.get('username') is not None:
        try:          
            if request.method == "GET":
                nama = request.GET.get('nama')
                print(nama)
            cursor = conn.cursor()
            if request.method == "POST":
                print()
            else:
                cursor.execute(
                    """
                    
                    """
                )
                daftar_paket = cursor.fetchall()
                list_paket_lain = [
                    {
                        
                    }
                ]
                return render(request, 'main:langganan', {"list_paket_lain":list_paket_lain})
            conn.commit()
            return redirect('main:langganan')

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

    return redirect('main:show_trailer')

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

def show_tayangan(request, id_tayangan, id_tayangan):
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
