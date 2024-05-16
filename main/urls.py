from django.urls import path
from main.views import *

app_name = 'main'

urlpatterns = [
    path('daftar_kontributor/', daftar_kontributor, name='daftar_kontributor'),
    path('langganan/', langganan, name='langganan'),
    path('halaman_beli/', halaman_beli, name='halaman_beli'),
    path('login/', show_login, name='show_login'),
    path('register/', show_register, name='show_register'),
    path('', show_home, name="show_home"),
    path('unduhan/', daftar_unduhan, name='daftar_unduhan'),
    path('delete-unduhan/', delete_unduhan, name='delete_unduhan'),
    path('tambah-unduhan/', tambah_unduhan, name='tambah_unduhan'),
    path('clear-error/', clear_error, name='clear_error'),
    path('favorit/', daftar_favorit, name='daftar_favorit'),
    path('isi-daftar-favorit/<str:judul>/', isi_daftar_favorit, name='isi_daftar_favorit'),
    path('delete-daftar-favorit/', delete_daftar_favorit, name='delete_daftar_favorit'),
    path('delete-dari-favorit/', delete_dari_favorit, name='delete_dari_favorit'),
    path('add-to-favorit/', add_to_favorit, name='add_to_favorit'),
    path('trailer/', show_trailer, name="show_trailer"),
    path('tayangan/', show_tayangan, name="show_tayangan"),
    path('episode/', show_episode, name="show_episode"),
]