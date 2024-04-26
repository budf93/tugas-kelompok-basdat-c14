from django.urls import path
from main.views import show_login,show_register,show_home

app_name = 'main'

urlpatterns = [
    path('login/', show_login, name='show_login'),
    path('register/', show_register, name='show_register'),
    path('', show_home, name="show_home")
]