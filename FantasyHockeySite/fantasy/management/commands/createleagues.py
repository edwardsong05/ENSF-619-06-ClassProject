from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from fantasy.models import FantasyLeague, FantasyTeam, \
                            Participates, LeagueCommissioner, SkaterTeams, \
                            GoalieTeams, NhlSkaters, NhlGoalies
import names
import random
import string

class Command(BaseCommand):
    help = 'Creates random users, leagues, and teams'
    numUsers = 20
    numLeagues = 10
    numLeagueParticipants=10

    def handle(self, *args, ** options):
        GoalieTeams.objects.all().delete()
        SkaterTeams.objects.all().delete()
        FantasyTeam.objects.all().delete()
        LeagueCommissioner.objects.all().delete()
        Participates.objects.all().delete()
        FantasyLeague.objects.all().delete()
        get_user_model().objects.all().delete()
        self.createUsers()
        self.createLeagues()
        self.insertPlayers()

    def insertGoalie(self, playerIds, goalies, league, team):
        while True:
            goalie = goalies[random.randint(0,len(goalies)-1)]
            if goalie.id.id in playerIds:
                    continue
            print("Added to team ", team.fantasy_team_name, ": goalie", goalie.id.id)
            #goalieobj = GoalieTeams.objects.create(fantasy_league_name=league, team_id=team, playerid=goalie.id)
            goalieobj = GoalieTeams.objects.create(team_id=team, playerid=goalie.id)
            goalieobj.save()
            playerIds.append(goalie.id.id)
            break

    def insertSkater(self, playerIds, skaters, league, team):
        while True:
            skater = skaters[random.randint(0,len(skaters)-1)]
            if skater.id.id in playerIds:
                continue
            print("Added to team", team.fantasy_team_name, ": skater", skater.id.id)
            #skaterobj = SkaterTeams.objects.create(fantasy_league_name=league, team_id=team, playerid=skater.id)
            skaterobj = SkaterTeams.objects.create(team_id=team, playerid=skater.id)
            skaterobj.save()
            playerIds.append(skater.id.id)
            break

    def insertPlayers(self):
        goalies = NhlGoalies.objects.all()
        skaters = NhlSkaters.objects.all()
        defences = NhlSkaters.objects.filter(defencemen_flag=1)
        rights = NhlSkaters.objects.filter(right_wing_flag=1)
        lefts = NhlSkaters.objects.filter(left_wing_flag=1)
        centers = NhlSkaters.objects.filter(center_flag=1)

        for league in FantasyLeague.objects.all():
            maxPlayers = league.maximum_number_of_players
            minGoalies = league.minimum_number_of_goalies
            minDef = league.minimum_number_of_defencemen
            minRight = league.minimum_number_of_right_wing
            minLeft = league.minimum_number_of_left_wing
            minCenter = league.minimum_number_of_center
            for team in FantasyTeam.objects.filter(fantasy_league_name=league.fantasy_league_name):
                playerIds = []

                #add the minimums for each team
                for i in range(minGoalies):
                    self.insertGoalie(playerIds, goalies, league, team)

                for i in range(minDef):
                    self.insertSkater(playerIds, defences, league, team)

                for i in range(minRight):
                    self.insertSkater(playerIds, rights, league, team)

                for i in range(minLeft):
                    self.insertSkater(playerIds, lefts, league, team)

                for i in range(minCenter):
                    self.insertSkater(playerIds, centers, league, team)

                #fill the remaining team members
                for i in range(maxPlayers-minGoalies-minDef-minRight-minLeft-minCenter):
                    #insert skaters to goalies at a 10:1 ratio
                    if random.randint(0,10) == 0:
                        self.insertGoalie(playerIds, goalies, league, team)
                    else:
                        self.insertSkater(playerIds, skaters, league, team)

    def createUsers(self):
        usernames = []
        for i in range(self.numUsers):
            while True:
                fname = names.get_first_name()
                lname = names.get_last_name()
                username = fname.lower()+lname
                if username in usernames:
                    continue
                email = username+"@hockey.com"
                user = get_user_model().objects.create_user(username=username,
                                                     email=email,
                                                     password='pass',
                                                     first_name = fname,
                                                     last_name = lname)
                user.save()
                break
            usernames.append(username)
            print("Added user:", username)

    def genRandomNum(self):
        return random.random()*2-1

    def genFunName(self):
        #A fun random name for teams and leagues
        ##random words from https://github.com/classam/silly/blob/master/silly/main.py
        nouns = ['onion','chimp','blister','poop','britches','mystery','boat'
                 'bench','secret','mouse','house','butt','hunter','fisher','bean',
                 'harvest','mixer','hand','finger','nose','eye','belly','jean',
                 'plan','disk','horse','staple','face','arm','cheek','monkey']
        adjectives = ['heroic','magnificent','mighty','amazing','wonderful',
                      'fantastic','incredible','spectacular','tremendous',
                      'throbbing','enormous','terrific','wondrous','spectacular',
                      'big','tiny','small','mighty','musky','sky','transparent',
                      'opaque','light','dark','sassy','scary','extraneous','huge',]
        name1 = adjectives[random.randint(0,len(adjectives)-1)].capitalize()
        name2 = nouns[random.randint(0,len(nouns)-1)].capitalize()
        return name1 + " " + name2

    def createLeagues(self):
        leaguenames = []
        usernames = [user.username for user in get_user_model().objects.all()]
        for i in range(self.numLeagues):
            while True:
                comExists = False

                leaguename = self.genFunName()
                if leaguename in leaguenames:
                    continue
                cusername = usernames[random.randint(0,len(usernames)-1)]
                cuser = get_user_model().objects.get(username=cusername)
                if not LeagueCommissioner.objects.filter(userid = cuser).exists():
                    commissioner = LeagueCommissioner.objects.create(userid = cuser)
                else:
                    commissioner = LeagueCommissioner.objects.get(userid = cuser)
                    comExists = True
                league = FantasyLeague.objects.create(
                        fantasy_league_name=leaguename,
                        goals_weight = self.genRandomNum(),
                        assists_weight = self.genRandomNum(),
                        powerplay_goals_weight = self.genRandomNum(),
                        powerplay_points_weight = self.genRandomNum(),
                        shorthanded_goals_weight = self.genRandomNum(),
                        shorthanded_points_weight = self.genRandomNum(),
                        plus_minus_weight = self.genRandomNum(),
                        penalty_minutes_weight = self.genRandomNum(),
                        game_winning_goals_weight = self.genRandomNum(),
                        shots_on_goal_weight = self.genRandomNum(),
                        wins_weight = self.genRandomNum(),
                        losses_weight = self.genRandomNum(),
                        overtime_losses_weight = self.genRandomNum(),
                        shots_against_weight = self.genRandomNum(),
                        saves_weight = self.genRandomNum(),
                        goals_against_weight = self.genRandomNum(),
                        saves_percentage_weight = self.genRandomNum(),
                        shutouts_weight = self.genRandomNum(),
                        maximum_number_of_players = random.randrange(30,50),
                        minimum_number_of_goalies = random.randrange(1,5),
                        minimum_number_of_defencemen = random.randrange(1,2),
                        minimum_number_of_right_wing = random.randrange(1,2),
                        minimum_number_of_left_wing = random.randrange(1,2),
                        minimum_number_of_center = random.randrange(1,2),
                        fantasy_league_invite_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6)),
                        commissionerid = commissioner)
                participate = Participates.objects.create(fantasy_league_name = league,
                                                          userid = cuser)
                if not comExists:
                    commissioner.save()
                league.save()
                participate.save()
                leaguenames.append(leaguename)
                print("\nAdded league:", leaguename)

                #insert people into the league
                leagueusernames = []
                leagueusernames.append(cusername)

                teamnames = []
                #team names should not be the same as the leaguename
                teamnames.append(leaguename)
                for i in range(self.numLeagueParticipants):
                    while True:
                        pusername = usernames[random.randint(0,len(usernames)-1)]
                        if pusername in leagueusernames:
                            continue
                        puser = get_user_model().objects.get(username=pusername)
                        participate = Participates.objects.create(fantasy_league_name = league,
                                                          userid = puser)
                        participate.save()
                        leagueusernames.append(pusername)
                        print("Added user:", pusername, "to league:", leaguename)

                        while True:
                            teamname = self.genFunName()
                            if teamname in teamnames:
                                continue
                            team = FantasyTeam.objects.create(fantasy_team_name = teamname,
                                                              fantasy_league_name = league,
                                                              fantasy_points = 0,
                                                              userid = puser)
                            team.save()
                            teamnames.append(teamname)
                            print("Added team:", teamname, "to league:", leaguename)
                            break
                        print("Added user:", pusername, "to league:", leaguename)
                        break
                break