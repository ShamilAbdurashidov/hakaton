from django.urls import path
from django.contrib.auth import views as auth_views

from users.views import *


app_name = 'users'


urlpatterns = [
    path('login/', login, name='login'),
    path('logout/', logout, name='logout'),
    path('password/change/', password_change, name='password_change'),
]
