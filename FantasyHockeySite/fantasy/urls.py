from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('nhl_players/', views.nhl_players, name='nhl_players'),
    path('nhl_teams/', views.nhl_teams, name='nhl_teams')
]