from django.urls import path
from main.views import daftar_kontributor, langganan, halaman_beli
from main.views import show_register,show_home, daftar_favorit, daftar_unduhan, show_daftar_tayangan, show_episode, show_tayangan, insert_ulasan, compute_riwayat_nonton

app_name = 'main'

urlpatterns = [
    path('daftar_kontributor/', daftar_kontributor, name='daftar_kontributor'),
    path('langganan/', langganan, name='langganan'),
    path('halaman_beli/', halaman_beli, name='halaman_beli'),
    path('register/', show_register, name='show_register'),
    path('', show_home, name="show_home"),
    path('unduhan/', daftar_unduhan, name='daftar_unduhan'),
    path('favorit/', daftar_favorit, name='daftar_favorit'),
    path('daftar_tayangan/', show_daftar_tayangan, name="show_daftar_tayangan"),
    path('tayangan/<str:id_tayangan>', show_tayangan, name="show_tayangan"),
    path('episode/', show_episode, name="show_episode"),
    path('insert_ulasan/', insert_ulasan, name="insert_ulasan"),
    path('compute_riwayat_nonton/', compute_riwayat_nonton, name="compute_riwayat_nonton"),
]