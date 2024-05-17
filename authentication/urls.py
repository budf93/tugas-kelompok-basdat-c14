from django.urls import path
from authentication.views import *
app_name = 'authentication'

urlpatterns = [
    path('login/', login, name='login'),
    path('logout/',logout,name='logout'),
    path('',redir_homepage, name="redir_homepage"),
    path('register/',register_pengguna, name="register_pengguna"),

]