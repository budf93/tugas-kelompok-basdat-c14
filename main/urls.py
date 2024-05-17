from django.urls import path
from main.views import daftar_kontributor, langganan, halaman_beli
from main.views import show_login,show_register,show_home, daftar_favorit, daftar_unduhan, show_trailer, show_episode, show_tayangan, insert_ulasan

app_name = 'main'

urlpatterns = [
    path('daftar_kontributor/', daftar_kontributor, name='daftar_kontributor'),
    path('langganan/', langganan, name='langganan'),
    path('halaman_beli/', halaman_beli, name='halaman_beli'),
    path('login/', show_login, name='show_login'),
    path('register/', show_register, name='show_register'),
    path('', show_home, name="show_home"),
    path('unduhan/', daftar_unduhan, name='daftar_unduhan'),
    path('favorit/', daftar_favorit, name='daftar_favorit'),
    path('trailer/', show_trailer, name="show_trailer"),
    path('tayangan/<str:id_tayangan>', show_tayangan, name="show_tayangan"),
    path('episode/', show_episode, name="show_episode"),
    path('insert_ulasan/', insert_ulasan, name="insert_ulasan"),
]