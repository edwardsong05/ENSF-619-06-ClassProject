from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import NhlPlayers, NhlTeam, NhlSkaters, NhlGoalies, FantasyLeague, LeagueCommissioner, Participates, FantasyTeam


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
    leagues = Participates.objects.filter(userid=u_id)

    if not leagues.exists():
        return HttpResponse('You are not participating in any leagues')
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

        # populate with players
        goalies = set()
        min_goalies = league.minimum_number_of_goalies
        while True:
            temp = NhlGoalies.objects.order_by('?').first()
            if temp.id.id in goalies:
                continue
            else:
                goalies.add(temp.id.id)
                Goalie_Teams.objects.create(team_id=ft) # unfinished
        return HttpResponse('Sucessfully created fantasy team: \"' + n + '\" with randomly selected players')
    else:
        return HttpResponse('The team name:\"' + n + '\" already exists within the league, team was not created')
