from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from fantasy.models import FantasyLeague, FantasyTeam, \
                            Participates, LeagueCommissioner, SkaterTeams, \
                            GoalieTeams, NhlSkaters, NhlGoalies
from decimal import Decimal
class Command(BaseCommand):
    help = 'Creates random users, leagues, and teams'
    numUsers = 20
    numLeagues = 10
    numLeagueParticipants=10
    
    def handle(self, *args, ** options):
        for league in FantasyLeague.objects.all():
            
            goals_weight = league.goals_weight
            assists_weight = league.assists_weight 
            powerplay_goals_weight = league.powerplay_goals_weight 
            powerplay_points_weight = league.powerplay_goals_weight 
            shorthanded_goals_weight = league.shorthanded_goals_weight 
            shorthanded_points_weight = league.shorthanded_points_weight 
            plus_minus_weight = league.plus_minus_weight
            penalty_minutes_weight = league.penalty_minutes_weight 
            game_winning_goals_weight = league.game_winning_goals_weight 
            shots_on_goal_weight = league.shots_on_goal_weight 
            wins_weight = league.wins_weight 
            losses_weight = league.losses_weight 
            overtime_losses_weight = league.overtime_losses_weight 
            shots_against_weight = league.shots_against_weight
            saves_weight = league.saves_weight 
            goals_against_weight = league.goals_against_weight 
            saves_percentage_weight = league.saves_percentage_weight 
            goals_against_average_weight = league.goals_against_average_weight 
            shutouts_weight = league.shutouts_weight 
            
            for team in FantasyTeam.objects.filter(fantasy_league_name=league).all():
                print("League:", league.fantasy_league_name, "Team:", team.fantasy_team_name)
                points = 0;
                for skater in SkaterTeams.objects.filter(team_id=team.id):
                    print("Team:", team.fantasy_team_name, "Skater:", skater.id)
                    nhlskater = NhlSkaters.objects.filter(id=skater.playerid).first()
                    points += nhlskater.goals*goals_weight
                    points += nhlskater.assists*assists_weight
                    points += nhlskater.powerplay_goals*powerplay_goals_weight
                    points += nhlskater.powerplay_points*powerplay_points_weight
                    points += nhlskater.shorthanded_goals*shorthanded_goals_weight
                    points += nhlskater.shorthanded_points*shorthanded_points_weight
                    points += nhlskater.plus_minus*plus_minus_weight
                    points += nhlskater.penalty_minutes*penalty_minutes_weight
                    points += nhlskater.game_winning_goals*game_winning_goals_weight
                    points += nhlskater.shots_on_goal*shots_on_goal_weight
                for goalie in GoalieTeams.objects.filter(team_id=team.id):
                    print("Team:", team.fantasy_team_name, "Goalie:", goalie.id)
                    nhlgoalie = NhlGoalies.objects.filter(id=goalie.playerid).first()
                    points += nhlgoalie.wins*wins_weight
                    points += nhlgoalie.losses*losses_weight
                    points += nhlgoalie.overtime_losses*overtime_losses_weight
                    points += nhlgoalie.shots_against*shots_against_weight
                    points += nhlgoalie.saves*saves_weight
                    goals_against = nhlgoalie.shots_against - nhlgoalie.saves
                    points += goals_against*goals_against_weight
                    saves_percentage = nhlgoalie.saves/nhlgoalie.shots_against
                    points += Decimal(saves_percentage)*saves_percentage_weight
                    points += nhlgoalie.shutouts*shutouts_weight
                print("Team:", team.fantasy_team_name, "Points:", points)
                team.fantasy_points = points
                team.save()