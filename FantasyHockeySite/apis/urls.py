# -*- coding: utf-8 -*-
"""
Created on Sat Mar 30 14:06:04 2019

@author: Eiden
"""

from django.urls import path
from apis import views
#from rest_framework.urlpatterns import format_suffix_patterns

urlpatterns = [
    path('leagues/', views.ListAllLeaguesView.as_view(), name="leagues-all"),
    path('leagues/<str:pk>/', views.ListTeamsInLeagueView.as_view(), name="teams-by-league"),
    path('teams/', views.ListAllTeamsView.as_view(), name="teams-all"),
    path('teams/<int:pk>/', views.ListAllTeamPlayersView.as_view(), name="players-by-fantasy-team"),
    path('nhlteams/', views.ListAllNhlTeamsView.as_view(), name="nhlteams-all"),
    path('nhlteams/<str:pk>/', views.ListPlayersInNhlTeamView.as_view(), name="nhlplayer-by-nhlteam")
]
#urlpatterns = format_suffix_patterns(urlpatterns)