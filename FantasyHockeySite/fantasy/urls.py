from django.urls import path

from . import views

app_name = 'fantasy'

urlpatterns = [
    path('index', views.index, name='index'),
    path('index/nhl_players/', views.nhl_players, name='nhl_players'),
    path('index/nhl_teams/', views.nhl_teams, name='nhl_teams'),
    path('index/search_nhl_player/', views.search_nhl_player, name='search_nhl_player'),
    path('index/search_player/', views.search_player, name='search_player'),
    path('index/create_fantasy_league/', views.create_fantasy_league, name='create_fantasy_league'),
    path('index/create_league/', views.create_league, name='create_league'),
    path('index/view_fantasy_league_invite_code/', views.view_fantasy_league_invite_code, name='view_fantasy_league_invite_code'),
    path('index/join_fantasy_league/', views.join_fantasy_league, name='join_fantasy_league'),
    path('index/join_league/', views.join_league, name='join_league'),
]