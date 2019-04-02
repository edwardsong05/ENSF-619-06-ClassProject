from fantasy.models import FantasyLeague, FantasyTeam, NhlPlayers, \
    SkaterTeams, GoalieTeams, NhlSkaters, NhlGoalies, NhlTeam
from apis import serializers
from rest_framework import generics
from rest_framework.views import APIView
from django.http import Http404
from rest_framework.response import Response
from rest_framework.decorators import permission_classes
from rest_framework import permissions
from django.core.exceptions import ObjectDoesNotExist
from decimal import Decimal

class ListAllLeaguesView(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = FantasyLeague.objects.all()
    serializer_class = serializers.LeaguesSerializer

class ListAllNhlTeamsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = NhlTeam.objects.all()
    serializer_class = serializers.NhlTeamsSerializer


@permission_classes((permissions.AllowAny,))
class ListPlayersInNhlTeamView(APIView):
    def get_object(self, pk):
        try:
            team = NhlTeam.objects.get(team_name=pk)
            players = NhlPlayers.objects.filter(team_name=pk)
            for player in players:
                if NhlSkaters.objects.filter(id=player.id).exists():
                    nhlskater = NhlSkaters.objects.get(id=player.id)
                    if nhlskater.center_flag:
                        player.position = "Center"
                    elif nhlskater.left_wing_flag:
                        player.position = "Left Wing"
                    elif nhlskater.right_wing_flag:
                        player.position = "Right Wing"
                    elif nhlskater.defencemen_flag:
                        player.position = "Defenceman"
                else:
                    player.position='Goalie'
                    
            return players
        except ObjectDoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None, **kwargs):
        queryset = self.get_object(pk)
        serializer = serializers.NhlPlayersSerializer(queryset, many=True)
        return Response(serializer.data)

@permission_classes((permissions.AllowAny,))
class ListTeamsInLeagueView(APIView):
    def get_object(self, pk):
        try:
            league = FantasyLeague.objects.get(fantasy_league_name=pk)
            teams = FantasyTeam.objects.filter(fantasy_league_name=league.fantasy_league_name)
            return teams
        except ObjectDoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None, **kwargs):
        teams = self.get_object(pk)
        serializer = serializers.TeamsSerializer(teams, many=True)
        return Response(serializer.data)


class ListAllTeamsView(generics.ListAPIView):
    """
    Provides a get method handler.
    """
    queryset = FantasyTeam.objects.all()
    serializer_class = serializers.TeamsSerializer
    
@permission_classes((permissions.AllowAny,))
class ListAllTeamPlayersView(APIView):
    def get_object(self, pk):
        try:
            team = FantasyTeam.objects.get(id=pk)
            
            #get weights for point calculation
            league = FantasyLeague.objects.get(fantasy_league_name=team.fantasy_league_name.fantasy_league_name)
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
            shutouts_weight = league.shutouts_weight 

            fantasyPoints = dict()
            position=dict()
            #calc skater points
            skaters = SkaterTeams.objects.filter(team_id=team.id)
            for skater in skaters:
                points = 0
                nhlskater = NhlSkaters.objects.get(id=skater.playerid)
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
                if nhlskater.center_flag:
                    position[skater.playerid.id] = "Center"
                elif nhlskater.left_wing_flag:
                    position[skater.playerid.id] = "Left Wing"
                elif nhlskater.right_wing_flag:
                    position[skater.playerid.id] = "Right Wing"
                elif nhlskater.defencemen_flag:
                    position[skater.playerid.id] = "Defenceman"
                fantasyPoints[skater.playerid.id] = points

            #calc goalie points
            goalies = GoalieTeams.objects.filter(team_id=team.id)
            for goalie in goalies:
                points = 0
                nhlgoalie = NhlGoalies.objects.get(id=goalie.playerid)
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
                position[goalie.playerid.id] = "Goalie"
                fantasyPoints[goalie.playerid.id] = points

            #get nhl player objects, assign the points and position to them
            players = NhlPlayers.objects.filter(id__in=fantasyPoints.keys())
            for player in players:
                player.fantasy_points = fantasyPoints[player.id]
                player.position = position[player.id]
            return players
        except ObjectDoesNotExist:
            raise Http404
    
    def get(self, request, pk, format=None, **kwargs):
        players = self.get_object(pk)
        serializer = serializers.FantasyPlayersSerializer(players, many=True)
        return Response(serializer.data)