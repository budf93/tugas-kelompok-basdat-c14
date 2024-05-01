from django.urls import path
from main.views import show_login,show_register,show_home, show_trailer, show_tayangan, show_episode

app_name = 'main'

urlpatterns = [
    path('login/', show_login, name='show_login'),
    path('register/', show_register, name='show_register'),
    path('', show_home, name="show_home"),
    path('trailer/', show_trailer, name="show_trailer"),
    path('tayangan/', show_tayangan, name="show_tayangan"),
    path('episode/', show_episode, name="show_episode"),
]