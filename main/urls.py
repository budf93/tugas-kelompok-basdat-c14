from django.urls import path
from main.views import show_login,show_register,show_home, daftar_favorit, daftar_unduhan

app_name = 'main'

urlpatterns = [
    path('login/', show_login, name='show_login'),
    path('register/', show_register, name='show_register'),
    path('', show_home, name="show_home"),
    path('unduhan/', daftar_unduhan, name='daftar_unduhan'),
    path('favorit/', daftar_favorit, name='daftar_favorit')
]