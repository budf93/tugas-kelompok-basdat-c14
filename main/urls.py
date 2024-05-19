from django.urls import path
from main.views import *

app_name = 'main'

urlpatterns = [
    path('daftar_kontributor/', daftar_kontributor, name='daftar_kontributor'),
    path('langganan/', langganan, name='langganan'),
    path('halaman_beli/', halaman_beli, name='halaman_beli'),
    path('register/', show_register, name='show_register'),
    path('', show_home, name="show_home"),
    path('unduhan/', daftar_unduhan, name='daftar_unduhan'),
    path('delete-unduhan/', delete_unduhan, name='delete_unduhan'),
    path('tambah-unduhan/', tambah_unduhan, name='tambah_unduhan'),
    path('favorit/', daftar_favorit, name='daftar_favorit'),
    path('isi-daftar-favorit/<str:judul>/', isi_daftar_favorit, name='isi_daftar_favorit'),
    path('delete-daftar-favorit/', delete_daftar_favorit, name='delete_daftar_favorit'),
    path('delete-dari-favorit/', delete_dari_favorit, name='delete_dari_favorit'),
    path('add-to-favorit/', add_to_favorit, name='add_to_favorit'),
    path('show_daftar_tayangan/', show_daftar_tayangan, name="show_daftar_tayangan"),
    path('tayangan/<str:id_tayangan>', show_tayangan, name="show_tayangan"),
    path('show_episode/<str:id_tayangan>/<str:judul>/<str:sub_judul>/', show_episode, name="show_episode"),
    path('insert_ulasan/', insert_ulasan, name="insert_ulasan"),
    path('compute_riwayat_nonton/', compute_riwayat_nonton, name="compute_riwayat_nonton"),
    path('search_tayangan/', search_tayangan, name='search_tayangan'),
]