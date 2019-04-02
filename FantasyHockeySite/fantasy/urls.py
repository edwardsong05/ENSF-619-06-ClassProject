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
    path('index/edit_fantasy_league_rules/', views.edit_fantasy_league_rules, name='edit_fantasy_league_rules'),
    path('index/edit_fantasy_league_rules/<str:league_name>', views.edit_league_rules, name='edit_league_rules'),
    path('index/edit_fantasy_league_rules/<str:league_name>/update_rules', views.update_rules, name='update_rules'),
    path('index/view_fantasy_league_invite_code/', views.view_fantasy_league_invite_code, name='view_fantasy_league_invite_code'),
    path('index/join_fantasy_league/', views.join_fantasy_league, name='join_fantasy_league'),
    path('index/join_league/', views.join_league, name='join_league'),
    path('index/create_fantasy_team/', views.create_fantasy_team_show_leagues, name='create_fantasy_team_show_leagues'),
    path('index/create_fantasy_team/<str:league_name>/', views.create_fantasy_team, name='create_fantasy_team'),
    path('index/create_fantasy_team/<str:league_name>/create_team/', views.create_team, name='create_team'),
    path('index/edit_fantasy_teams/', views.edit_fantasy_teams, name='edit_fantasy_teams'),
    path('index/edit_fantasy_teams/<int:team_id>/', views.select_action, name='select_action'),
    path('index/edit_fantasy_teams/<int:team_id>/add_goalie/', views.add_goalie, name='add_goalie'),
    path('index/edit_fantasy_teams/<int:team_id>/add_center/', views.add_center, name='add_center'),
    path('index/edit_fantasy_teams/<int:team_id>/add_left_wing/', views.add_left_wing, name='add_left_wing'),
    path('index/edit_fantasy_teams/<int:team_id>/add_right_wing/', views.add_right_wing, name='add_right_wing'),
    path('index/edit_fantasy_teams/<int:team_id>/add_defencemen/', views.add_defencemen, name='add_defencemen'),
    path('index/edit_fantasy_teams/<int:team_id>/add_player/<int:nhl_id>/', views.add, name='add'),
    path('index/edit_fantasy_teams/<int:team_id>/remove_goalie/', views.remove_goalie, name='remove_goalie'),
    path('index/edit_fantasy_teams/<int:team_id>/remove_center/', views.remove_center, name='remove_center'),
    path('index/edit_fantasy_teams/<int:team_id>/remove_left_wing/', views.remove_left_wing, name='remove_left_wing'),
    path('index/edit_fantasy_teams/<int:team_id>/remove_right_wing/', views.remove_right_wing, name='remove_right_wing'),
    path('index/edit_fantasy_teams/<int:team_id>/remove_defencemen/', views.remove_defencemen, name='remove_defencemen'),
    path('index/edit_fantasy_teams/<int:team_id>/remove_player/<int:nhl_id>/', views.remove, name='remove'),
    path('index/view_fantasy_teams/', views.view_fantasy_teams, name='view_fantasy_teams'),
    path('index/view_fantasy_teams/<int:teamid>/', views.view_fantasy_team_players, name='view_fantasy_team_players'),
    path('index/view_fantasy_leagues/', views.view_fantasy_leagues, name='view_fantasy_leagues'),
    path('index/view_fantasy_leagues/<str:f_name>', views.view_fantasy_league_teams, name='view_fantasy_league_teams'),
]
