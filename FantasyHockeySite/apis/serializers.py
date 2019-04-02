from rest_framework import serializers
from fantasy.models import FantasyLeague, FantasyTeam, NhlPlayers, NhlTeam

class NhlPlayersSerializer(serializers.ModelSerializer):
    position = serializers.SerializerMethodField()
    
    def get_position(self, obj):
        return obj.position

    class Meta:
        model = NhlPlayers
        fields = ("name", "jersey_number", "games_played", "position")

class NhlTeamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NhlTeam
        fields = ("team_name","wins","losses")

class LeaguesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FantasyLeague
        fields = ("fantasy_league_name",)
        
class TeamsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FantasyTeam
        fields = ("id", "fantasy_team_name", "fantasy_points")

class FantasyPlayersSerializer(serializers.ModelSerializer):
    fantasy_points = serializers.SerializerMethodField()
    position = serializers.SerializerMethodField()

    def get_fantasy_points(self, obj):
        return obj.fantasy_points

    def get_position(self, obj):
        return obj.position

    class Meta:
        model = NhlPlayers
        fields = ("id", "name", "position", "fantasy_points")