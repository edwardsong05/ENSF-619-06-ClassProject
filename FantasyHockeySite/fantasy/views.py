import decimal

from django.shortcuts import render
from django.db import connection
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError

from .models import NhlPlayers, NhlTeam, NhlSkaters, NhlGoalies, FantasyLeague, LeagueCommissioner, Participates, FantasyTeam, GoalieTeams, SkaterTeams


# Create your views here.
def index(request):
    return render(request, 'fantasy/index.html')


def nhl_players(request):
    skaters = NhlSkaters.objects.select_related('id').all().order_by('id__team_name', 'id__name')
    goalies = NhlGoalies.objects.select_related('id').all().order_by('id__team_name', 'id__name')
    return render(request, 'fantasy/display_players.html', {'skaters': skaters, 'goalies': goalies})


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
        return render(request, 'fantasy/display_message.html', {'message': 'No parameters entered, search was not performed'})
    teams = NhlTeam.objects.filter(team_name__icontains=tn)
    if jn == '':
        skaters = NhlSkaters.objects.select_related('id').filter(id__team_name__in=teams, id__name__icontains=n)
        goalies = NhlGoalies.objects.select_related('id').filter(id__team_name__in=teams, id__name__icontains=n)
    else:
        skaters = NhlSkaters.objects.select_related('id').filter(id__team_name__in=teams, id__jersey_number=jn, id__name__icontains=n)
        goalies = NhlGoalies.objects.select_related('id').filter(id__team_name__in=teams, id__jersey_number=jn, id__name__icontains=n)
    return render(request, 'fantasy/display_players.html', {'skaters': skaters, 'goalies': goalies})


def create_fantasy_league(request):
    return render(request, 'fantasy/create_fantasy_league.html')


def create_league(request):
    n = request.POST['name'].strip()
    c = request.POST['code']
    # check for unique name and code
    if FantasyLeague.objects.filter(fantasy_league_name=n).exists():
        return render(request, 'fantasy/display_message.html', {'message': 'League name \"' + n + '\" already exists'})
    elif FantasyLeague.objects.filter(fantasy_league_invite_code=c):
        return render(request, 'fantasy/display_message.html', {'message': 'Invite code \"' + c + '\" already exists'})
    elif n == '' or c == '':
        return render(request, 'fantasy/display_message.html', {'message': 'Please enter a name and an invite code'})
    else:
        u_id = request.user.id
        u_id = get_object_or_404(get_user_model(), pk=u_id)
        if not LeagueCommissioner.objects.filter(userid=u_id).exists():
            commissioner = LeagueCommissioner.objects.create(userid=u_id)
        else:
            commissioner = get_object_or_404(LeagueCommissioner, pk=u_id)

        league = FantasyLeague.objects.create(fantasy_league_name=n, fantasy_league_invite_code=c, commissionerid=commissioner)
        return render(request, 'fantasy/display_message.html', {'message': 'Fantasy league \"' + n + '\" was sucessfully created, please edit the rules before inviting people to join the league'})


def view_fantasy_league_invite_code(request):
    u_id = request.user.id
    if not LeagueCommissioner.objects.filter(userid=u_id).exists():
        return render(request, 'fantasy/display_message.html', {'message': 'You are currently not a league commisioner'})
    else:
        commissioner = get_object_or_404(LeagueCommissioner, pk=u_id)
        leagues = FantasyLeague.objects.filter(commissionerid=commissioner)
        return render(request, 'fantasy/view_fantasy_league_invite_code.html', {'query_results': leagues})


def join_fantasy_league(request):
    return render(request, 'fantasy/join_fantasy_league.html')


def join_league(request):
    c = request.POST['code']
    # check for valid code
    if not FantasyLeague.objects.filter(fantasy_league_invite_code=c).exists():
        return render(request, 'fantasy/display_message.html', {'message': 'Fantasy league with invite code \"' + c + '\" does not exist'})

    # check if user is already participating in the league
    u_id = request.user.id
    u_id = get_object_or_404(get_user_model(), pk=u_id)
    league = get_object_or_404(FantasyLeague, fantasy_league_invite_code=c)
    if Participates.objects.filter(userid=u_id).filter(fantasy_league_name=league).exists():
        return render(request, 'fantasy/display_message.html', {'message': 'You are already participating in this fantasy league'})

    p = Participates.objects.create(userid=u_id, fantasy_league_name=league)
    return render(request, 'fantasy/display_message.html', {'message': 'Sucessfully joined fantasy league \"' + league.fantasy_league_name + '\"'})


def create_fantasy_team_show_leagues(request):
    u_id = request.user.id
    u_id = get_object_or_404(get_user_model(), pk=u_id)
    # get fantasy leagues where the user doesn't have a fantasy team
    teams = FantasyTeam.objects.filter(userid=u_id).values_list('fantasy_league_name', flat=True)
    leagues = Participates.objects.filter(userid=u_id).exclude(fantasy_league_name__in=teams)

    if not leagues.exists():
        return render(request, 'fantasy/display_message.html', {'message': 'You have no available teams to create'})
    else:
        return render(request, 'fantasy/create_fantasy_team_show_leagues.html', {'query_results': leagues})


def create_fantasy_team(request, league_name):
    league = get_object_or_404(FantasyLeague, pk=league_name)
    return render(request, 'fantasy/create_fantasy_team.html', {'league': league})


def create_team(request, league_name):
    n = request.POST['name']
    if not FantasyTeam.objects.filter(fantasy_team_name=n, fantasy_league_name=league_name).exists():
        # create the fantasy team
        u_id = request.user.id
        u_id = get_object_or_404(get_user_model(), pk=u_id)
        league = get_object_or_404(FantasyLeague, fantasy_league_name=league_name)
        ft = FantasyTeam.objects.create(fantasy_team_name=n, fantasy_league_name=league, userid=u_id)

        # populate with randomly selected goalies
        min_goalies = league.minimum_number_of_goalies
        temp = NhlGoalies.objects.order_by('?')[:min_goalies]
        for item in temp:
            GoalieTeams.objects.create(playerid=item.id, team_id=ft)

        # populate with randomly selected defencemen
        min_def = league.minimum_number_of_defencemen
        temp = NhlSkaters.objects.filter(defencemen_flag=1).order_by('?')[:min_def]
        for item in temp:
            SkaterTeams.objects.create(playerid=item.id, team_id=ft)

        # populate with randomly selected right wing
        min_right = league.minimum_number_of_right_wing
        temp = NhlSkaters.objects.filter(right_wing_flag=1).order_by('?')[:min_right]
        for item in temp:
            SkaterTeams.objects.create(playerid=item.id, team_id=ft)

        # populate with randomly selected left wing
        min_left = league.minimum_number_of_left_wing
        temp = NhlSkaters.objects.filter(left_wing_flag=1).order_by('?')[:min_left]
        for item in temp:
            SkaterTeams.objects.create(playerid=item.id, team_id=ft)

        # populate with randomly selected center
        min_cen = league.minimum_number_of_center
        temp = NhlSkaters.objects.filter(center_flag=1).order_by('?')[:min_cen]
        for item in temp:
            SkaterTeams.objects.create(playerid=item.id, team_id=ft)

        return render(request, 'fantasy/display_message.html', {'message': 'Sucessfully created fantasy team \"' + n  + '\" with randomly selected players'})
    else:
        return render(request, 'fantasy/display_message.html', {'message': 'Team name \"' + n  + '\" already exists within the league, team was not created'})


def edit_fantasy_teams(request):
    u_id = request.user.id
    u_id = get_object_or_404(get_user_model(), pk=u_id)
    teams = FantasyTeam.objects.filter(userid=u_id)
    return render(request, 'fantasy/edit_fantasy_teams.html', {'teams': teams})


def select_action(request, team_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    return render(request, 'fantasy/select_action.html', {'team': team})


def add_goalie(request, team_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    max_players = team.fantasy_league_name.maximum_number_of_players
    count = SkaterTeams.objects.filter(team_id=team.id).count()
    count += GoalieTeams.objects.filter(team_id=team.id).count()
    if max_players <= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the maximum ('+ str(max_players) +') allowable number of players for this league'})
    current_goalies = GoalieTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    available_goalies = NhlGoalies.objects.all().exclude(id__in=current_goalies)
    order_by = request.GET.get('order_by', 'defaultOrderField')
    if order_by=='team_name' or order_by=='defaultOrderField':
        available_goalies = available_goalies.order_by('id__team_name', 'id__name')
    elif order_by=='name':
        available_goalies = available_goalies.order_by('id__name', 'id__team_name')
    return render(request, 'fantasy/add_goalie.html', {'team': team, 'available_goalies': available_goalies})


def add_center(request, team_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    max_players = team.fantasy_league_name.maximum_number_of_players
    count = SkaterTeams.objects.filter(team_id=team.id).count()
    count += GoalieTeams.objects.filter(team_id=team.id).count()
    if max_players <= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the maximum ('+ str(max_players) +') allowable number of players for this league'})
    current_skaters = SkaterTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    available_skaters = NhlSkaters.objects.filter(center_flag=1).exclude(id__in=current_skaters)
    order_by = request.GET.get('order_by', 'defaultOrderField')
    if order_by=='team_name' or order_by=='defaultOrderField':
        available_skaters = available_skaters.order_by('id__team_name', 'id__name')
    elif order_by=='name':
        available_skaters = available_skaters.order_by('id__name', 'id__team_name')
    return render(request, 'fantasy/add_skater.html', {'team': team, 'available_skaters': available_skaters})


def add_left_wing(request, team_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    max_players = team.fantasy_league_name.maximum_number_of_players
    count = SkaterTeams.objects.filter(team_id=team.id).count()
    count += GoalieTeams.objects.filter(team_id=team.id).count()
    if max_players <= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the maximum ('+ str(max_players) +') allowable number of players for this league'})
    current_skaters = SkaterTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    available_skaters = NhlSkaters.objects.filter(left_wing_flag=1).exclude(id__in=current_skaters)
    order_by = request.GET.get('order_by', 'defaultOrderField')
    if order_by=='team_name' or order_by=='defaultOrderField':
        available_skaters = available_skaters.order_by('id__team_name', 'id__name')
    elif order_by=='name':
        available_skaters = available_skaters.order_by('id__name', 'id__team_name')
    return render(request, 'fantasy/add_skater.html', {'team': team, 'available_skaters': available_skaters})


def add_right_wing(request, team_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    max_players = team.fantasy_league_name.maximum_number_of_players
    count = SkaterTeams.objects.filter(team_id=team.id).count()
    count += GoalieTeams.objects.filter(team_id=team.id).count()
    if max_players <= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the maximum ('+ str(max_players) +') allowable number of players for this league'})
    current_skaters = SkaterTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    available_skaters = NhlSkaters.objects.filter(right_wing_flag=1).exclude(id__in=current_skaters)
    order_by = request.GET.get('order_by', 'defaultOrderField')
    if order_by=='team_name' or order_by=='defaultOrderField':
        available_skaters = available_skaters.order_by('id__team_name', 'id__name')
    elif order_by=='name':
        available_skaters = available_skaters.order_by('id__name', 'id__team_name')
    return render(request, 'fantasy/add_skater.html', {'team': team, 'available_skaters': available_skaters})


def add_defencemen(request, team_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    max_players = team.fantasy_league_name.maximum_number_of_players
    count = SkaterTeams.objects.filter(team_id=team.id).count()
    count += GoalieTeams.objects.filter(team_id=team.id).count()
    if max_players <= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the maximum ('+ str(max_players) +') allowable number of players for this league'})
    current_skaters = SkaterTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    available_skaters = NhlSkaters.objects.filter(defencemen_flag=1).exclude(id__in=current_skaters)
    order_by = request.GET.get('order_by', 'defaultOrderField')
    if order_by=='team_name' or order_by=='defaultOrderField':
        available_skaters = available_skaters.order_by('id__team_name', 'id__name')
    elif order_by=='name':
        available_skaters = available_skaters.order_by('id__name', 'id__team_name')
    return render(request, 'fantasy/add_skater.html', {'team': team, 'available_skaters': available_skaters})


def add(request, team_id, nhl_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    # check if the player to add is a goalie
    if NhlGoalies.objects.filter(pk=nhl_id).exists():
        goalie = get_object_or_404(NhlGoalies, pk=nhl_id)
        # check if the goalie is already on the team
        if not GoalieTeams.objects.filter(playerid=goalie.id, team_id=team).exists():
            GoalieTeams.objects.create(playerid=goalie.id, team_id=team)
            return render(request, 'fantasy/display_message.html', {'message': 'Goalie was sucessfully added to the team', 'returnToTeamEdit':True, 'team_id':str(team_id)})
        else:
            return render(request, 'fantasy/display_message.html', {'message': 'Goalie was already on the team, goalie was not inserted', 'returnToTeamEdit':True, 'team_id':str(team_id)})
    # check if the player to add is a skater
    elif NhlSkaters.objects.filter(pk=nhl_id).exists():
        skater = get_object_or_404(NhlSkaters, pk=nhl_id)
        # check if skater is already on the team
        if not SkaterTeams.objects.filter(playerid=skater.id, team_id=team).exists():
            SkaterTeams.objects.create(playerid=skater.id, team_id=team)
            return render(request, 'fantasy/display_message.html', {'message': 'Skater was sucessfully added to the team', 'returnToTeamEdit':True, 'team_id':str(team_id)})
        else:
            return render(request,'fantasy/display_message.html', {'message': 'Skater was already on the team, skater was not inserted', 'returnToTeamEdit':True, 'team_id':str(team_id)})
    else:
        return render(request, 'fantasy/display_message.html', {'message': 'An error has occured: player was not added to the team', 'returnToTeamEdit':True, 'team_id':str(team_id)})


def remove_goalie(request, team_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    min_goalies = team.fantasy_league_name.minimum_number_of_goalies
    count = GoalieTeams.objects.filter(team_id=team.id).count()
    if min_goalies >= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the minimum (' + str(min_goalies) + ') allowable number of goalies for this league', 'returnToTeamEdit':True, 'team_id':str(team_id)})
    current_goalies = GoalieTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    goalies = NhlGoalies.objects.filter(id__in=current_goalies)
    return render(request, 'fantasy/remove_goalie.html', {'team': team, 'goalies': goalies})


def remove_center(request, team_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    min_center = team.fantasy_league_name.minimum_number_of_center
    skaters = SkaterTeams.objects.filter(team_id=team.id).values_list('playerid', flat=True)
    centers = NhlSkaters.objects.filter(id__in=skaters, center_flag=1)
    if min_center >= centers.count():
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the minimum (' + str(min_center) + ') allowable number of centers for this league', 'returnToTeamEdit':True, 'team_id':str(team_id)})
    return render(request, 'fantasy/remove_skater.html', {'team': team, 'skaters': centers})


def remove_left_wing(request, team_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    min_left = team.fantasy_league_name.minimum_number_of_left_wing
    skaters = SkaterTeams.objects.filter(team_id=team.id).values_list('playerid', flat=True)
    lefts = NhlSkaters.objects.filter(id__in=skaters, left_wing_flag=1)
    if min_left >= lefts.count():
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the minimum (' + str(min_left) + ') allowable number of left wings for this league', 'returnToTeamEdit':True, 'team_id':str(team_id)})
    return render(request, 'fantasy/remove_skater.html', {'team': team, 'skaters': lefts})


def remove_right_wing(request, team_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    min_right = team.fantasy_league_name.minimum_number_of_center
    skaters = SkaterTeams.objects.filter(team_id=team.id).values_list('playerid', flat=True)
    rights = NhlSkaters.objects.filter(id__in=skaters, right_wing_flag=1)
    if min_right >= rights.count():
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the minimum (' + str(min_right) + ') allowable number of right wings for this league', 'returnToTeamEdit':True, 'team_id':str(team_id)})
    return render(request, 'fantasy/remove_skater.html', {'team': team, 'skaters': rights})


def remove_defencemen(request, team_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    min_def = team.fantasy_league_name.minimum_number_of_defencemen
    skaters = SkaterTeams.objects.filter(team_id=team.id).values_list('playerid', flat=True)
    defences = NhlSkaters.objects.filter(id__in=skaters, defencemen_flag=1)
    if min_def >= defences.count():
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the minimum (' + str(min_def) + ') allowable number of defencemen for this league', 'returnToTeamEdit':True, 'team_id':str(team_id)})
    return render(request, 'fantasy/remove_skater.html', {'team': team, 'skaters': defences})


def remove(request, team_id, nhl_id):
    team = get_object_or_404(FantasyTeam, pk=team_id)
    val = validate_user(request, team)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    if NhlGoalies.objects.filter(pk=nhl_id).exists():
        goalie = get_object_or_404(NhlPlayers, pk=nhl_id)
        get_object_or_404(GoalieTeams, playerid=goalie, team_id=team).delete()
        return render(request, 'fantasy/display_message.html', {'message': 'Goalie was sucessfully removed from the team', 'returnToTeamEdit':True, 'team_id':str(team_id)})
    elif NhlSkaters.objects.filter(pk=nhl_id).exists():
        skater = get_object_or_404(NhlPlayers, pk=nhl_id)
        get_object_or_404(SkaterTeams, playerid=skater, team_id=team).delete()
        return render(request, 'fantasy/display_message.html', {'message': 'Skater was sucessfully removed from the team', 'returnToTeamEdit':True, 'team_id':str(team_id)})
    else:
        return render(request, 'fantasy/display_message.html', {'message': 'An error has occured: player was not removed from the team', 'returnToTeamEdit':True, 'team_id':str(team_id)})


def view_fantasy_teams(request):
    u_id = request.user.id
    u_id = get_object_or_404(get_user_model(), pk=u_id)
    teams = FantasyTeam.objects.filter(userid=u_id)

    # derive the team stats for each fantasy team
    for team in teams:
        skater_ids = SkaterTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
        goalie_ids = GoalieTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
        skaters = NhlSkaters.objects.filter(id__in=skater_ids)
        goalies = NhlGoalies.objects.filter(id__in=goalie_ids)

        # skater variables
        goals = assists = powerplay_goals = powerplay_points = shorthanded_goals = shorthanded_points = plus_minus = 0
        penalty_minutes = game_winning_goals = shots_on_goal = 0
        for skater in skaters:
            goals += skater.goals
            assists += skater.assists
            powerplay_goals += skater.powerplay_goals
            shorthanded_goals += skater.shorthanded_goals
            shorthanded_points += skater.shorthanded_points
            plus_minus += skater.plus_minus
            penalty_minutes += skater.penalty_minutes
            game_winning_goals += skater.game_winning_goals
            shots_on_goal += skater.shots_on_goal

        # goalie variables
        wins = losses = overtime_losses = shots_against = saves = shutouts = 0
        for goalie in goalies:
            wins += goalie.wins
            losses += goalie.losses
            overtime_losses += goalie.overtime_losses
            shots_against += goalie.shots_against
            saves += goalie.saves
            shutouts += goalie.shutouts

        team.goals = goals
        team.assists = assists
        team.powerplay_goals = powerplay_goals
        team.powerplay_points = powerplay_points
        team.shorthanded_goals = shorthanded_goals
        team.shorthanded_points = shorthanded_points
        team.plus_minus = plus_minus
        team.penalty_minutes = penalty_minutes
        team.game_winning_goals = game_winning_goals
        team.shots_on_goal = shots_on_goal
        team.wins = wins
        team.losses = losses
        team.overtime_losses = overtime_losses
        team.shots_against = shots_against
        team.saves = saves
        team.shutouts = shutouts

    return render(request, 'fantasy/view_fantasy_teams.html', {'teams': teams})


def view_fantasy_team_players(request, teamid):
    skater_ids = SkaterTeams.objects.filter(team_id=teamid).values_list('playerid', flat=True)
    skaters = NhlSkaters.objects.filter(id__in=skater_ids)
    goalies_ids = GoalieTeams.objects.filter(team_id=teamid).values_list('playerid', flat=True)
    goalies = NhlGoalies.objects.filter(id__in=goalies_ids)
    return render(request, 'fantasy/display_players.html', {'skaters': skaters, 'goalies': goalies})


def view_fantasy_leagues(request):
    u_id = request.user.id
    u_id = get_object_or_404(get_user_model(), pk=u_id)
    league_names = Participates.objects.filter(userid=u_id).values_list('fantasy_league_name', flat=True)
    leagues = FantasyLeague.objects.filter(fantasy_league_name__in=league_names)
    return render(request, 'fantasy/view_fantasy_leagues.html', {'leagues': leagues})


def view_fantasy_league_teams(request, f_name):
    league = get_object_or_404(FantasyLeague, pk=f_name)
    teams = FantasyTeam.objects.select_related('userid').filter(fantasy_league_name=f_name).order_by('-fantasy_points')
    return render(request, 'fantasy/view_fantasy_league_teams.html', {'teams': teams, 'league': league})


def edit_fantasy_league_rules(request):
    u_id = request.user.id
    u_id = get_object_or_404(get_user_model(), pk=u_id)
    # check if the user is a commisioner (has leagues)
    if not LeagueCommissioner.objects.filter(userid=u_id).exists():
        return render(request, 'fantasy/display_message.html', {'message': 'You have no leagues to edit'})
    else:
        # get leagues where the user can edit the rules (no current teams in the league)
        commissioner = get_object_or_404(LeagueCommissioner, pk=u_id)
        leagues = FantasyLeague.objects.filter(commissionerid=commissioner)
        par = Participates.objects.filter(fantasy_league_name__in=leagues).values_list('fantasy_league_name', flat=True)
        edit_leagues = leagues.exclude(fantasy_league_name__in=par)
        if edit_leagues.exists():
            return render(request, 'fantasy/edit_fantasy_league_rules.html', {'leagues': edit_leagues})
        else:
            return render(request, 'fantasy/display_message.html', {'message': 'All leagues currently have participants, unable to edit leagues which have participants'})


def edit_league_rules(request, league_name):
    league = get_object_or_404(FantasyLeague, pk=league_name)
    # check if the user is the commissioner and is allowed to edit the league
    val = validate_user(request, league)
    if not val[0]:
        return render(request, 'fantasy/display_message.html', {'message': val[1]})
    return render(request, 'fantasy/edit_league_rules.html', {'league': league})


def update_rules(request, league_name):
    league = get_object_or_404(FantasyLeague, pk=league_name)

    goals_weight = request.POST['goals_weight'].strip()
    if goals_weight == '':
        pass
    else:
        try:
            league.goals_weight = float(goals_weight)
        except ValueError:
            pass

    assists_weight = request.POST['assists_weight'].strip()
    if assists_weight == '':
        pass
    else:
        try:
            league.assists_weight = float(assists_weight)
        except ValueError:
            pass

    powerplay_goals_weight = request.POST['powerplay_goals_weight'].strip()
    if powerplay_goals_weight == '':
        pass
    else:
        try:
            league.powerplay_goals_weight = float(powerplay_goals_weight)
        except ValueError:
            pass

    powerplay_points_weight = request.POST['powerplay_points_weight'].strip()
    if powerplay_points_weight == '':
        pass
    else:
        try:
            league.powerplay_points_weight = float(powerplay_points_weight)
        except ValueError:
            pass

    shorthanded_goals_weight = request.POST['shorthanded_goals_weight'].strip()
    if shorthanded_goals_weight == '':
        pass
    else:
        try:
            league.shorthanded_goals_weight == float(shorthanded_goals_weight)
        except ValueError:
            pass

    plus_minus_weight = request.POST['plus_minus_weight'].strip()
    if plus_minus_weight == '':
        pass
    else:
        try:
            league.plus_minus_weight = float(plus_minus_weight)
        except ValueError:
            pass

    penalty_minutes_weight = request.POST['penalty_minutes_weight'].strip()
    if penalty_minutes_weight == '':
        pass
    else:
        try:
            league.penalty_minutes_weight = float(penalty_minutes_weight)
        except ValueError:
            pass

    game_winning_goals_weight = request.POST['game_winning_goals_weight'].strip()
    if game_winning_goals_weight == '':
        pass
    else:
        try:
            league.game_winning_goals_weight = float(game_winning_goals_weight)
        except ValueError:
            pass

    shots_on_goal_weight = request.POST['shots_on_goal_weight'].strip()
    if shots_on_goal_weight == '':
        pass
    else:
        try:
            league.shots_on_goal_weight = float(shots_on_goal_weight)
        except ValueError:
            pass

    wins_weight = request.POST['wins_weight'].strip()
    if wins_weight == '':
        pass
    else:
        try:
            league.wins_weight = float(wins_weight)
        except ValueError:
            pass

    losses_weight = request.POST['losses_weight'].strip()
    if losses_weight == '':
        pass
    else:
        try:
            league.losses_weight = float(losses_weight)
        except ValueError:
            pass

    overtime_losses_weight = request.POST['overtime_losses_weight'].strip()
    if overtime_losses_weight == '':
        pass
    else:
        try:
            league.overtime_losses_weight = float(overtime_losses_weight)
        except ValueError:
            pass

    shots_against_weight = request.POST['shots_against_weight'].strip()
    if shots_against_weight == '':
        pass
    else:
        try:
            league.shots_against_weight = float(shots_against_weight)
        except ValueError:
            pass

    saves_weight = request.POST['saves_weight'].strip()
    if saves_weight == '':
        pass
    else:
        try:
            league.saves_weight = float(saves_weight)
        except ValueError:
            pass

    goals_against_weight = request.POST['goals_against_weight'].strip()
    if goals_against_weight == '':
        pass
    else:
        try:
            league.goals_against_weight = float(goals_against_weight)
        except ValueError:
            pass

    saves_percentage_weight = request.POST['saves_percentage_weight'].strip()
    if saves_percentage_weight == '':
        pass
    else:
        try:
            league.saves_percentage_weight = float(saves_percentage_weight)
        except ValueError:
            pass

    shutouts_weight = request.POST['shutouts_weight'].strip()
    if shutouts_weight == '':
        pass
    else:
        try:
            league.shutouts_weight = float(shutouts_weight)
        except ValueError:
            pass

    # calculate maximum number of players and minimum number of players
    # ensure max is never smaller than min
    min_players = 0
    max_players = 0

    maximum_number_of_players = request.POST['maximum_number_of_players'].strip()
    if maximum_number_of_players == '':
        pass
    else:
        try:
            league.maximum_number_of_players = int(maximum_number_of_players)
        except ValueError:
            pass
    max_players = league.maximum_number_of_players

    minimum_number_of_goalies = request.POST['minimum_number_of_goalies'].strip()
    if minimum_number_of_goalies == '':
        pass
    else:
        try:
            league.minimum_number_of_goalies = int(minimum_number_of_goalies)
        except ValueError:
            pass
    min_players += league.minimum_number_of_goalies

    minimum_number_of_defencemen = request.POST['minimum_number_of_defencemen'].strip()
    if minimum_number_of_defencemen == '':
        pass
    else:
        try:
            league.minimum_number_of_defencemen = int(minimum_number_of_defencemen)
        except ValueError:
            pass
    min_players += league.minimum_number_of_defencemen

    minimum_number_of_right_wing = request.POST['minimum_number_of_right_wing'].strip()
    if minimum_number_of_right_wing == '':
        pass
    else:
        try:
            league.minimum_number_of_right_wing = int(minimum_number_of_right_wing)
        except ValueError:
            pass
    min_players += league.minimum_number_of_right_wing

    minimum_number_of_left_wing = request.POST['minimum_number_of_left_wing'].strip()
    if minimum_number_of_left_wing == '':
        pass
    else:
        try:
            league.minimum_number_of_left_wing = int(minimum_number_of_left_wing)
        except ValueError:
            pass
    min_players += league.minimum_number_of_left_wing

    minimum_number_of_center = request.POST['minimum_number_of_center'].strip()
    if minimum_number_of_center == '':
        pass
    else:
        try:
            league.minimum_number_of_center = int(minimum_number_of_center)
            min_players += int(minimum_number_of_center)
        except ValueError:
            pass
    min_players += league.minimum_number_of_center

    if min_players > max_players:
        return render(request, 'fantasy/display_message.html', {'message': 'Maximum number of players must be equal to or exceed total of minimum number of players, changes were not made'})
    elif max_players == 0:
        return render(request, 'fantasy/display_message.html', {'message': 'Maximum number of players must be greater than zero, changes were not made'})
    else:
        try:
            league.save()
        except decimal.InvalidOperation:
            return render(request, 'fantasy/display_message.html', {'message': 'Invalid decimal value was provided, changes were not made'})
        return render(request, 'fantasy/display_message.html', {'message': 'Sucessfully made changes to league rules'})


def validate_user(request, obj):
    u_id = request.user.id
    u_id = get_object_or_404(get_user_model(), pk=u_id)

    if isinstance(obj, FantasyTeam):
        user = obj.userid
        if user != u_id:
            return (False, 'You do not have permission to edit this team')
    elif isinstance(obj, FantasyLeague):
        user = obj.commissionerid.userid
        if user != u_id:
            return (False, 'You do not have permission to edit this league')
    return (True, None)
