from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import NhlPlayers, NhlTeam, NhlSkaters, NhlGoalies, FantasyLeague, LeagueCommissioner, Participates, FantasyTeam, GoalieTeams, SkaterTeams


# Create your views here.
def index(request):
    return render(request, 'fantasy/index.html')


def nhl_players(request):
    query_results = NhlPlayers.objects.all()
    return render(request, 'fantasy/nhl_players.html', {'query_results': query_results})


def nhl_teams(request):
    query_results = NhlTeam.objects.all()
    return render(request, 'fantasy/nhl_team.html', {'query_results': query_results})


def search_nhl_player(request):
    return render(request, 'fantasy/search_nhl_player.html')


def search_player(request):
    tn = request.GET.get('team_name').strip()
    jn = request.GET.get('jersey_number').strip()
    n = request.GET.get('name').strip()
    if tn == '' and jn == '' and n == '':
        return HttpResponse("Please enter some parameters")
    teams = NhlTeam.objects.filter(team_name__icontains=tn)
    skaters = NhlSkaters.objects.select_related('id').filter(id__team_name__in=teams, id__jersey_number__icontains=jn, id__name__icontains=n)
    goalies = NhlGoalies.objects.select_related('id').filter(id__team_name__in=teams, id__jersey_number__icontains=jn, id__name__icontains=n)
    return render(request, 'fantasy/search_player.html', {'query_results1': skaters, 'query_results2': goalies})


def create_fantasy_league(request):
    return render(request, 'fantasy/create_fantasy_league.html')


def create_league(request):
    n = request.GET.get('name').strip()
    c = request.GET.get('code')
    # check for unique name and code
    if FantasyLeague.objects.filter(fantasy_league_name=n).exists():
        return HttpResponse('League Name ' + n + ' already exists')
    elif FantasyLeague.objects.filter(fantasy_league_invite_code=c):
        return HttpResponse('Duplicate invite code')
    elif n == '' and c == '':
        return HttpResponse('Please enter a name and an invite code')
    else:
        u_id = request.user.id
        u_id = get_user_model().objects.get(id=u_id)
        if not LeagueCommissioner.objects.filter(userid=u_id).exists():
            commissioner = LeagueCommissioner.objects.create(userid=u_id)
        else:
            commissioner = LeagueCommissioner.objects.get(userid=u_id)

        league = FantasyLeague.objects.create(fantasy_league_name=n, fantasy_league_invite_code=c, commissionerid=commissioner)
        return HttpResponse('Fantasy League ' + n + ' created')


def view_fantasy_league_invite_code(request):
    u_id = request.user.id
    if not LeagueCommissioner.objects.filter(userid=u_id).exists():
        return HttpResponse("You are not a League commisioner")
    else:
        commisioner = LeagueCommissioner.objects.get(userid=u_id)
        leagues = FantasyLeague.objects.filter(commissionerid=commisioner)
        return render(request, 'fantasy/view_fantasy_league_invite_code.html', {'query_results': leagues})


def join_fantasy_league(request):
    return render(request, 'fantasy/join_fantasy_league.html')


def join_league(request):
    c = request.GET.get('code')
    # check for valid code
    if not FantasyLeague.objects.filter(fantasy_league_invite_code=c).exists():
        return HttpResponse('Fantasy League does not exist')

    # check if user is already participating in the league
    u_id = request.user.id
    u_id = get_user_model().objects.get(id=u_id)
    league = FantasyLeague.objects.get(fantasy_league_invite_code=c)
    if Participates.objects.filter(userid=u_id).filter(fantasy_league_name=league).exists():
        return HttpResponse('You are already participating in this fantasy league')

    p = Participates.objects.create(userid=u_id, fantasy_league_name=league)
    return HttpResponse('Sucessfully joined Fantasy League')


def create_fantasy_team_show_leagues(request):
    u_id = request.user.id
    u_id = get_user_model().objects.get(id=u_id)
    # get fantasy leagues where the user doesn't have a fantasy team
    teams = FantasyTeam.objects.filter(userid=u_id).values_list('fantasy_league_name', flat=True)
    leagues = Participates.objects.filter(userid=u_id).exclude(fantasy_league_name__in=teams)

    if not leagues.exists():
        return HttpResponse('You have no available teams to create')
    else:
        return render(request, 'fantasy/create_fantasy_team_show_leagues.html', {'query_results': leagues})


def create_fantasy_team(request, league_name):
    league = get_object_or_404(FantasyLeague, pk=league_name)
    return render(request, 'fantasy/create_fantasy_team.html', {'league': league})


def create_team(request, league_name):
    n = request.GET.get('name')
    if not FantasyTeam.objects.filter(fantasy_team_name=n, fantasy_league_name=league_name).exists():
        # create the fantasy team
        u_id = request.user.id
        u_id = get_user_model().objects.get(id=u_id)
        league = FantasyLeague.objects.get(fantasy_league_name=league_name)
        ft = FantasyTeam.objects.create(fantasy_team_name=n, fantasy_league_name=league, userid=u_id)

        # populate with randomly selected goalies
        min_goalies = league.minimum_number_of_goalies
        temp = NhlGoalies.objects.order_by('?')[:min_goalies]
        for item in temp:
            GoalieTeams.objects.create(playerid=item.id, fantasy_league_name=league, team_id=ft)

        # populate with randomly selected defencemen
        min_def = league.minimum_number_of_defencemen
        temp = NhlSkaters.objects.filter(defencemen_flag=1).order_by('?')[:min_def]
        for item in temp:
            SkaterTeams.objects.create(playerid=item.id, fantasy_league_name=league, team_id=ft)

        # populate with randomly selected right wing
        min_right = league.minimum_number_of_right_wing
        temp = NhlSkaters.objects.filter(right_wing_flag=1).order_by('?')[:min_right]
        for item in temp:
            SkaterTeams.objects.create(playerid=item.id, fantasy_league_name=league, team_id=ft)

        # populate with randomly selected left wing
        min_left = league.minimum_number_of_left_wing
        temp = NhlSkaters.objects.filter(left_wing_flag=1).order_by('?')[:min_left]
        for item in temp:
            SkaterTeams.objects.create(playerid=item.id, fantasy_league_name=league, team_id=ft)

        # populate with randomly selected center
        min_cen = league.minimum_number_of_center
        temp = NhlSkaters.objects.filter(center_flag=1).order_by('?')[:min_cen]
        for item in temp:
            SkaterTeams.objects.create(playerid=item.id, fantasy_league_name=league, team_id=ft)

        return HttpResponse('Sucessfully created fantasy team: \"' + n + '\" with randomly selected players')
    else:
        return HttpResponse('The team name:\"' + n + '\" already exists within the league, team was not created')


def edit_fantasy_teams(request):
    u_id = request.user.id
    u_id = get_user_model().objects.get(id=u_id)
    teams = FantasyTeam.objects.filter(userid=u_id)
    return render(request, 'fantasy/edit_fantasy_teams.html', {'teams': teams})


def select_action(request, team_id):
    team = FantasyTeam.objects.get(pk=team_id)
    return render(request, 'fantasy/select_action.html', {'team': team})


def add_goalie(request, team_id):
    team = FantasyTeam.objects.get(pk=team_id)
    current_goalies = GoalieTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    available_goalies = NhlGoalies.objects.all().exclude(id__in=current_goalies)
    return render(request, 'fantasy/add_goalie.html', {'team': team, 'available_goalies': available_goalies})


def add(request, team_id, nhl_id):
    team = FantasyTeam.objects.get(pk=team_id)
    goalie = NhlGoalies.objects.get(pk=nhl_id)
    GoalieTeams.objects.create(playerid=goalie.id, fantasy_league_name=team.fantasy_league_name, team_id=team)
    return HttpResponse('Goalie was sucessfully added to the team')


def view_fantasy_teams(request):
    u_id = request.user.id
    u_id = get_user_model().objects.get(id=u_id)
    teams = FantasyTeam.objects.filter(userid=u_id)
    return render(request, 'fantasy/view_fantasy_teams.html', {'teams': teams})


def view_fantasy_team_players(request, teamid):
    skater_ids = SkaterTeams.objects.filter(team_id=teamid).values_list('playerid', flat=True)
    skaters = NhlSkaters.objects.filter(id__in=skater_ids)
    goalies_ids = GoalieTeams.objects.filter(team_id=teamid).values_list('playerid', flat=True)
    goalies = NhlGoalies.objects.filter(id__in=goalies_ids)
    return render(request, 'fantasy/search_player.html', {'query_results1': skaters, 'query_results2': goalies})
