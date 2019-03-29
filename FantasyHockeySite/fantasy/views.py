from django.shortcuts import render
from django.http import HttpResponse

from .models import NhlPlayers, NhlTeam


# Create your views here.
def index(request):
    # return HttpResponse("Hello, world. You're at the views index.")
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
    n = str(request.GET.get('name').strip())
    query_results = NhlPlayers.objects.get(name=n)
    return HttpResponse(n)
