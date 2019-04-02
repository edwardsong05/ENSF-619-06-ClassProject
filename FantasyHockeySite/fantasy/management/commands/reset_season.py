from django.core.management.base import BaseCommand, CommandError
from fantasy.models import NhlTeam, NhlPlayers, NhlSkaters, NhlGoalies, LeagueCommisioner, FantasyLeague, Participates, FantasyTeam, GoalieTeams, SkaterTeams


class Command(BaseCommand):
    help = 'Truncate NHL stats and Fantasy league related tables'

    def handle(self, *args, ** options):
        NhlTeam.objects.all().delete()
        NhlPlayers.objects.all().delete()
        NhlSkaters.objects.all().delete()
        NhlGoalies.objects.all().delete()
        LeagueCommisioner.objects.all().delete()
        FantasyLeague.objects.all().delete()
        Participates.objects.all().delete()
        FantasyTeam.objects.all().delete()
        GoalieTeams.objects.all().delete()
        SkaterTeams.objects.all().delete()
