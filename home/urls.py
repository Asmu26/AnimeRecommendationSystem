from django.contrib import admin
from django.urls import path
from home import views
from .views import *
from django.urls import path
from . import views



urlpatterns = [
    path('', views.landing, name='landing'),
    path('landing/', views.landing, name='landing'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.userlogin, name='login'),
    path('logout/', views.logoutuser, name='logout'),
    path('home/', views.home, name='home'),
    path('nav/', views.nav, name='nav'),
    path('aap/', views.aap, name='aap'),
    path('footer/', views.footer, name='footer'),
    path('csvadd/', views.csvadd, name='csvadd'),
    path('episode/<int:num>', views.epsiode, name='episode'),
    path('anime_detail/<int:pk>', views.anime_detail, name='anime_detail'),
    path('add-watchlist', views.add_watchlist, name='add_watchlist'),
    path('watchlist/', views.watchlists, name='watchlists'),
    path('notification-seen', views.notification_seen, name='notification-seen'),
    path('average-rating', views.average_rating, name='average_rating'),
    path('forgotpass/', views.forgotpass, name='forgotpass'),
    path('reset_password/<str:token>/', views.reset_password, name='reset_password'),
    path('anime_list/', views.anime_list, name='anime_list'),#genre
    path('add-watchlist', views.add_to_watchlist, name='add_to_watchlist'),
]