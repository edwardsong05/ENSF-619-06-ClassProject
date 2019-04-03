from django.shortcuts import render
from django.db import connection
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .models import NhlPlayers, NhlTeam, NhlSkaters, NhlGoalies, FantasyLeague, LeagueCommissioner, Participates, FantasyTeam, GoalieTeams, SkaterTeams, Participates


# Create your views here.
def index(request):
    return render(request, 'fantasy/index.html')


def nhl_players(request):
    skaters = NhlSkaters.objects.select_related('id').all()
    goalies = NhlGoalies.objects.select_related('id').all()
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
    skaters = NhlSkaters.objects.select_related('id').filter(id__team_name__in=teams, id__jersey_number=jn, id__name__icontains=n)
    goalies = NhlGoalies.objects.select_related('id').filter(id__team_name__in=teams, id__jersey_number=jn, id__name__icontains=n)
    return render(request, 'fantasy/display_players.html', {'skaters': skaters, 'goalies': goalies})


def create_fantasy_league(request):
    return render(request, 'fantasy/create_fantasy_league.html')


def create_league(request):
    n = request.GET.get('name').strip()
    c = request.GET.get('code')
    # check for unique name and code
    if FantasyLeague.objects.filter(fantasy_league_name=n).exists():
        return render(request, 'fantasy/display_message.html', {'message': 'League name \"' + n + '\" already exists'})
    elif FantasyLeague.objects.filter(fantasy_league_invite_code=c):
        return render(request, 'fantasy/display_message.html', {'message': 'Invite code \"' + c + '\" already exists'})
    elif n == '' or c == '':
        return render(request, 'fantasy/display_message.html', {'message': 'Please enter a name and an invite code'})
    else:
        u_id = request.user.id
        u_id = get_user_model().objects.get(id=u_id)
        if not LeagueCommissioner.objects.filter(userid=u_id).exists():
            commissioner = LeagueCommissioner.objects.create(userid=u_id)
        else:
            commissioner = LeagueCommissioner.objects.get(userid=u_id)

        league = FantasyLeague.objects.create(fantasy_league_name=n, fantasy_league_invite_code=c, commissionerid=commissioner)
        return render(request, 'fantasy/display_message.html', {'message': 'Fantasy league \"' + n + '\" was sucessfully created'})


def view_fantasy_league_invite_code(request):
    u_id = request.user.id
    if not LeagueCommissioner.objects.filter(userid=u_id).exists():
        return render(request, 'fantasy/display_message.html', {'message': 'You are currently not a league commisioner'})
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
        return render(request, 'fantasy/display_message.html', {'message': 'Fantasy league with invite code \"' + c + '\" does not exist'})

    # check if user is already participating in the league
    u_id = request.user.id
    u_id = get_user_model().objects.get(id=u_id)
    league = FantasyLeague.objects.get(fantasy_league_invite_code=c)
    if Participates.objects.filter(userid=u_id).filter(fantasy_league_name=league).exists():
        return render(request, 'fantasy/display_message.html', {'message': 'You are already participating in this fantasy league'})

    p = Participates.objects.create(userid=u_id, fantasy_league_name=league)
    return render(request, 'fantasy/display_message.html', {'message': 'Sucessfully joined fantasy league \"' + league.fantasy_league_name + '\"'})


def create_fantasy_team_show_leagues(request):
    u_id = request.user.id
    u_id = get_user_model().objects.get(id=u_id)
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

        return render(request, 'fantasy/display_message.html', {'message': 'Sucessfully created fantasy team \"' + n  + '\" with randomly selected players'})
    else:
        return render(request, 'fantasy/display_message.html', {'message': 'Team name \"' + n  + '\" already exists within the league, team was not created'})


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
    max_players = team.fantasy_league_name.maximum_number_of_players
    count = SkaterTeams.objects.filter(team_id=team.id).count()
    count += GoalieTeams.objects.filter(team_id=team.id).count()
    if max_players <= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the maximum ('+ str(max_players) +') allowable number of players for this league'})
    current_goalies = GoalieTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    available_goalies = NhlGoalies.objects.all().exclude(id__in=current_goalies)
    return render(request, 'fantasy/add_goalie.html', {'team': team, 'available_goalies': available_goalies})


def add_center(request, team_id):
    team = FantasyTeam.objects.get(pk=team_id)
    max_players = team.fantasy_league_name.maximum_number_of_players
    count = SkaterTeams.objects.filter(team_id=team.id).count()
    count += GoalieTeams.objects.filter(team_id=team.id).count()
    if max_players <= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the maximum ('+ str(max_players) +') allowable number of players for this league'})
    current_skaters = SkaterTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    available_skaters = NhlSkaters.objects.filter(center_flag=1).exclude(id__in=current_skaters)
    return render(request, 'fantasy/add_skater.html', {'team': team, 'available_skaters': available_skaters})


def add_left_wing(request, team_id):
    team = FantasyTeam.objects.get(pk=team_id)
    max_players = team.fantasy_league_name.maximum_number_of_players
    count = SkaterTeams.objects.filter(team_id=team.id).count()
    count += GoalieTeams.objects.filter(team_id=team.id).count()
    if max_players <= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the maximum ('+ str(max_players) +') allowable number of players for this league'})
    current_skaters = SkaterTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    available_skaters = NhlSkaters.objects.filter(left_wing_flag=1).exclude(id__in=current_skaters)
    return render(request, 'fantasy/add_skater.html', {'team': team, 'available_skaters': available_skaters})


def add_right_wing(request, team_id):
    team = FantasyTeam.objects.get(pk=team_id)
    max_players = team.fantasy_league_name.maximum_number_of_players
    count = SkaterTeams.objects.filter(team_id=team.id).count()
    count += GoalieTeams.objects.filter(team_id=team.id).count()
    if max_players <= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the maximum ('+ str(max_players) +') allowable number of players for this league'})
    current_skaters = SkaterTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    available_skaters = NhlSkaters.objects.filter(right_wing_flag=1).exclude(id__in=current_skaters)
    return render(request, 'fantasy/add_skater.html', {'team': team, 'available_skaters': available_skaters})


def add_defencemen(request, team_id):
    team = FantasyTeam.objects.get(pk=team_id)
    max_players = team.fantasy_league_name.maximum_number_of_players
    count = SkaterTeams.objects.filter(team_id=team.id).count()
    count += GoalieTeams.objects.filter(team_id=team.id).count()
    if max_players <= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the maximum ('+ str(max_players) +') allowable number of players for this league'})
    current_skaters = SkaterTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    available_skaters = NhlSkaters.objects.filter(defencemen_flag=1).exclude(id__in=current_skaters)
    return render(request, 'fantasy/add_skater.html', {'team': team, 'available_skaters': available_skaters})


def add(request, team_id, nhl_id):
    team = FantasyTeam.objects.get(pk=team_id)
    if NhlGoalies.objects.filter(pk=nhl_id).exists():
        goalie = NhlGoalies.objects.get(pk=nhl_id)
        GoalieTeams.objects.create(playerid=goalie.id, fantasy_league_name=team.fantasy_league_name, team_id=team)
        return render(request, 'fantasy/display_message.html', {'message': 'Goalie was sucessfully added to the team'})
    elif NhlSkaters.objects.filter(pk=nhl_id).exists():
        skater = NhlSkaters.objects.get(pk=nhl_id)
        SkaterTeams.objects.create(playerid=skater.id, fantasy_league_name=team.fantasy_league_name, team_id=team)
        return render(request, 'fantasy/display_message.html', {'message': 'Skater was sucessfully added to the team'})
    else:
        return render(request, 'fantasy/display_message.html', {'message': 'An error has occured: player was not added to the team'})


def remove_goalie(request, team_id):
    team = FantasyTeam.objects.get(pk=team_id)
    min_goalies = team.fantasy_league_name.minimum_number_of_goalies
    count = GoalieTeams.objects.filter(team_id=team.id).count()
    if min_goalies >= count:
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the minimum (' + str(min_goalies) + ') allowable number of goalies for this league'})
    current_goalies = GoalieTeams.objects.filter(team_id=team).values_list('playerid', flat=True)
    goalies = NhlGoalies.objects.filter(id__in=current_goalies)
    return render(request, 'fantasy/remove_goalie.html', {'team': team, 'goalies': goalies})


def remove_center(request, team_id):
    team = FantasyTeam.objects.get(pk=team_id)
    min_center = team.fantasy_league_name.minimum_number_of_center
    skaters = SkaterTeams.objects.filter(team_id=team.id).values_list('playerid', flat=True)
    centers = NhlSkaters.objects.filter(id__in=skaters, center_flag=1)
    if min_center >= centers.count():
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the minimum (' + str(min_center) + ') allowable number of centers for this league'})
    return render(request, 'fantasy/remove_skater.html', {'team': team, 'skaters': centers})


def remove_left_wing(request, team_id):
    team = FantasyTeam.objects.get(pk=team_id)
    min_left = team.fantasy_league_name.minimum_number_of_left_wing
    skaters = SkaterTeams.objects.filter(team_id=team.id).values_list('playerid', flat=True)
    lefts = NhlSkaters.objects.filter(id__in=skaters, left_wing_flag=1)
    if min_left >= lefts.count():
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the minimum (' + str(min_left) + ') allowable number of left wings for this league'})
    return render(request, 'fantasy/remove_skater.html', {'team': team, 'skaters': lefts})


def remove_right_wing(request, team_id):
    team = FantasyTeam.objects.get(pk=team_id)
    min_right = team.fantasy_league_name.minimum_number_of_center
    skaters = SkaterTeams.objects.filter(team_id=team.id).values_list('playerid', flat=True)
    rights = NhlSkaters.objects.filter(id__in=skaters, right_wing_flag=1)
    if min_right >= rights.count():
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the minimum (' + str(min_right) + ') allowable number of right wings for this league'})
    return render(request, 'fantasy/remove_skater.html', {'team': team, 'skaters': rights})


def remove_defencemen(request, team_id):
    team = FantasyTeam.objects.get(pk=team_id)
    min_def = team.fantasy_league_name.minimum_number_of_defencemen
    skaters = SkaterTeams.objects.filter(team_id=team.id).values_list('playerid', flat=True)
    defences = NhlSkaters.objects.filter(id__in=skaters, defencemen_flag=1)
    if min_def >= defences.count():
        return render(request, 'fantasy/display_message.html', {'message': 'You have reached the minimum (' + str(min_def) + ') allowable number of defencemen for this league'})
    return render(request, 'fantasy/remove_skater.html', {'team': team, 'skaters': defences})


def remove(request, team_id, nhl_id):
    team = FantasyTeam.objects.get(pk=team_id)
    if NhlGoalies.objects.filter(pk=nhl_id).exists():
        goalie = NhlPlayers.objects.get(pk=nhl_id)
        GoalieTeams.objects.get(playerid=goalie, team_id=team).delete()
        return render(request, 'fantasy/display_message.html', {'message': 'Goalie was sucessfully removed from the team'})
    elif NhlSkaters.objects.filter(pk=nhl_id).exists():
        skater = NhlPlayers.objects.get(pk=nhl_id)
        SkaterTeams.objects.get(playerid=skater, team_id=team).delete()
        return render(request, 'fantasy/display_message.html', {'message': 'Skater was sucessfully removed from the team'})
    else:
        return render(request, 'fantasy/display_message.html', {'message': 'An error has occured: player was not removed from the team'})


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
    return render(request, 'fantasy/display_players.html', {'skaters': skaters, 'goalies': goalies})


def view_fantasy_leagues(request):
    u_id = request.user.id
    u_id = get_user_model().objects.get(id=u_id)
    league_names = Participates.objects.filter(userid=u_id).values_list('fantasy_league_name', flat=True)
    leagues = FantasyLeague.objects.filter(fantasy_league_name__in=league_names)
    return render(request, 'fantasy/view_fantasy_leagues.html', {'leagues': leagues})


def view_fantasy_league_teams(request, f_name):
    teams = FantasyTeam.objects.select_related('userid').filter(fantasy_league_name=f_name)
    return render(request, 'fantasy/view_fantasy_league_teams.html', {'teams': teams})


def edit_fantasy_league_rules(request):
    u_id = request.user.id
    u_id = get_user_model().objects.get(id=u_id)
    # check if the user is a commisioner (has leagues)
    if not LeagueCommissioner.objects.filter(userid=u_id).exists():
        return render(request, 'fantasy/display_message.html', {'message': 'You have no leagues to edit'})
    else:
        # get leagues where the user can edit the rules (no current teams in the league)
        commissioner = LeagueCommissioner.objects.get(pk=u_id)
        leagues = FantasyLeague.objects.filter(commissionerid=commissioner)
        par = Participates.objects.filter(fantasy_league_name__in=leagues).values_list('fantasy_league_name', flat=True)
        edit_leagues = leagues.exclude(fantasy_league_name__in=par)
        if edit_leagues.exists():
            return render(request, 'fantasy/edit_fantasy_league_rules.html', {'leagues': edit_leagues})
        else:
            return render(request, 'fantasy/display_message.html', {'message': 'All leagues currently have participants, unable to edit leagues which have participants'})


def edit_league_rules(request, league_name):
    league = FantasyLeague.objects.get(pk=league_name)
    return render(request, 'fantasy/edit_league_rules.html', {'league': league})


def update_rules(request, league_name):
    league = FantasyLeague.objects.get(pk=league_name)

    goals_weight = request.GET.get('goals_weight').strip()
    if goals_weight == '':
        pass
    else:
        try:
            league.goals_weight = float(goals_weight)
        except ValueError:
            pass

    assists_weight = request.GET.get('assists_weight').strip()
    if assists_weight == '':
        pass
    else:
        try:
            league.assists_weight = float(assists_weight)
        except ValueError:
            pass

    powerplay_goals_weight = request.GET.get('powerplay_goals_weight').strip()
    if powerplay_goals_weight == '':
        pass
    else:
        try:
            league.powerplay_goals_weight = float(powerplay_goals_weight)
        except ValueError:
            pass

    powerplay_points_weight = request.GET.get('powerplay_points_weight').strip()
    if powerplay_points_weight == '':
        pass
    else:
        try:
            league.powerplay_points_weight = float(powerplay_points_weight)
        except ValueError:
            pass

    shorthanded_goals_weight = request.GET.get('shorthanded_goals_weight').strip()
    if shorthanded_goals_weight == '':
        pass
    else:
        try:
            league.shorthanded_goals_weight == float(shorthanded_goals_weight)
        except ValueError:
            pass

    plus_minus_weight = request.GET.get('plus_minus_weight').strip()
    if plus_minus_weight == '':
        pass
    else:
        try:
            league.plus_minus_weight = float(plus_minus_weight)
        except ValueError:
            pass

    penalty_minutes_weight = request.GET.get('penalty_minutes_weight').strip()
    if penalty_minutes_weight == '':
        pass
    else:
        try:
            league.penalty_minutes_weight = float(penalty_minutes_weight)
        except ValueError:
            pass

    game_winning_goals_weight = request.GET.get('game_winning_goals_weight').strip()
    if game_winning_goals_weight == '':
        pass
    else:
        try:
            league.game_winning_goals_weight = float(game_winning_goals_weight)
        except ValueError:
            pass

    shots_on_goal_weight = request.GET.get('shots_on_goal_weight').strip()
    if shots_on_goal_weight == '':
        pass
    else:
        try:
            league.shots_on_goal_weight = float(shots_on_goal_weight)
        except ValueError:
            pass

    wins_weight = request.GET.get('wins_weight').strip()
    if wins_weight == '':
        pass
    else:
        try:
            league.wins_weight = float(wins_weight)
        except ValueError:
            pass

    losses_weight = request.GET.get('losses_weight').strip()
    if losses_weight == '':
        pass
    else:
        try:
            league.losses_weight = float(losses_weight)
        except ValueError:
            pass

    overtime_losses_weight = request.GET.get('overtime_losses_weight').strip()
    if overtime_losses_weight == '':
        pass
    else:
        try:
            league.overtime_losses_weight = float(overtime_losses_weight)
        except ValueError:
            pass

    shots_against_weight = request.GET.get('shots_against_weight').strip()
    if shots_against_weight == '':
        pass
    else:
        try:
            league.shots_against_weight = float(shots_against_weight)
        except ValueError:
            pass

    saves_weight = request.GET.get('saves_weight').strip()
    if saves_weight == '':
        pass
    else:
        try:
            league.saves_weight = float(saves_weight)
        except ValueError:
            pass

    goals_against_weight = request.GET.get('goals_against_weight').strip()
    if goals_against_weight == '':
        pass
    else:
        try:
            league.goals_against_weight = float(goals_against_weight)
        except ValueError:
            pass

    saves_percentage_weight = request.GET.get('saves_percentage_weight').strip()
    if saves_percentage_weight == '':
        pass
    else:
        try:
            league.saves_percentage_weight = float(saves_percentage_weight)
        except ValueError:
            pass

    #goals_against_average_weight = request.GET.get('goals_against_average_weight').strip()
    #if goals_against_average_weight == '':
    #    pass
    #else:
    #    try:
    #        league.goals_against_average_weight = float(goals_against_average_weight)
    #    except ValueError:
    #        pass

    shutouts_weight = request.GET.get('shutouts_weight').strip()
    if shutouts_weight == '':
        pass
    else:
        try:
            league.shutouts_weight = float(shutouts_weight)
        except ValueError:
            pass

    maximum_number_of_players = request.GET.get('maximum_number_of_players').strip()
    if maximum_number_of_players == '':
        pass
    else:
        try:
            league.maximum_number_of_players = int(maximum_number_of_players)
        except ValueError:
            pass

    minimum_number_of_goalies = request.GET.get('minimum_number_of_goalies').strip()
    if minimum_number_of_goalies == '':
        pass
    else:
        try:
            league.minimum_number_of_goalies = int(minimum_number_of_goalies)
        except ValueError:
            pass

    minimum_number_of_defencemen = request.GET.get('minimum_number_of_defencemen').strip()
    if minimum_number_of_defencemen == '':
        pass
    else:
        try:
            league.minimum_number_of_defencemen = int(minimum_number_of_defencemen)
        except ValueError:
            pass

    minimum_number_of_right_wing = request.GET.get('minimum_number_of_right_wing').strip()
    if minimum_number_of_right_wing == '':
        pass
    else:
        try:
            league.minimum_number_of_right_wing = int(minimum_number_of_right_wing)
        except ValueError:
            pass

    minimum_number_of_left_wing = request.GET.get('minimum_number_of_left_wing').strip()
    if minimum_number_of_left_wing == '':
        pass
    else:
        try:
            league.minimum_number_of_left_wing = int(minimum_number_of_left_wing)
        except ValueError:
            pass

    minimum_number_of_center = request.GET.get('minimum_number_of_center').strip()
    if minimum_number_of_center == '':
        pass
    else:
        try:
            league.minimum_number_of_center = int(minimum_number_of_center)
        except ValueError:
            pass

    league.save()
    return render(request, 'fantasy/display_message.html', {'message': 'Sucessfully made changes to league rules'})
