from django.urls import path
from main.views import show_main, daftar_kontributor, langganan, halaman_beli

app_name = 'main'

urlpatterns = [
    path('', show_main, name='show_main'),
    path('daftar_kontributor/', daftar_kontributor, name='daftar_kontributor'),
    path('langganan/', langganan, name='langganan'),
    path('halaman_beli/', halaman_beli, name='halaman_beli'),
]