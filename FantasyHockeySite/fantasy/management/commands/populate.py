from django.core.management.base import BaseCommand, CommandError
from fake_useragent import UserAgent
from django.conf import settings
import requests
import pandas as pd
import pymysql
from fantasy.models import NhlPlayers, NhlTeam, NhlSkaters, NhlGoalies, FantasyLeague, LeagueCommissioner, Participates, FantasyTeam, GoalieTeams, SkaterTeams, Participates

import os
import json
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class Command(BaseCommand):
    help = 'Updates models in the NHL Team table'

    def getRequest(self, url):
        # randomise user agent to prevent rate limit
        while True:
            try:
                ua = UserAgent()
                header = {'User-Agent':str(ua.random)}
                r = requests.get(url, headers = header, timeout = 10)
                break
            except Exception as e:
                # sometimes it will timeout and raise exception
                print(str(e))
        return r

    def handle(self, *args, ** options):
        print("RUNNING")
        # database connection params
        host_name = 'localhost'
        port_num = 3306
        user_name = 'root'
        db_name = 'fantasydb'
        with open(os.path.join(settings.BASE_DIR, 'secrets.json')) as secrets_file:
            secrets = json.load(secrets_file)
        try:
            psw = secrets['DB_PASSWORD']
        except KeyError:
            raise ImproperlyConfigured("DB PASSWORD NOT FOUND")
        baseURL = "https://statsapi.web.nhl.com"
        teamsURL = "https://statsapi.web.nhl.com/api/v1/teams"
        print(teamsURL)
        r = self.getRequest(teamsURL)
        teamsData = r.json()

        # get team stats
        dfTeams = pd.DataFrame(columns=['id','teamName','evGGARatio','faceOffWinPercentage',
                                        'faceOffsLost','faceOffsTaken','faceOffsWon',
                                        'gamesPlayed','goalsAgainstPerGame',
                                        'goalsPerGame','losses','ot','penaltyKillPercentage',
                                        'powerPlayGoals','powerPlayGoalsAgainst',
                                        'powerPlayOpportunities','powerPlayPercentage',
                                        'ptPctg','pts','savePctg','shootingPctg',
                                        'shotsAllowed','shotsPerGame','winLeadFirstPer',
                                        'winLeadSecondPer','winOppScoreFirst','winOutshootOpp',
                                        'winOutshotByOpp','winScoreFirst','wins'])

        listGoalies = []
        listSkaters = []

        for team in teamsData['teams']:
            teamURL = team['link']
            r = self.getRequest(baseURL + teamURL + "?expand=team.stats")
            print(team['name'], r.status_code)
            teamData = r.json()
            teamStats = teamData['teams'][0]['teamStats'][0]['splits'][0]['stat']
            teamStats['teamName'] = team['name']
            tempDf = pd.DataFrame.from_records([teamStats])
            dfTeams = dfTeams.append(tempDf, ignore_index=True, sort = False)




            teamURL = team['link']
            r = self.getRequest(baseURL + teamURL + "?expand=team.roster")
            print(team['name'], r.status_code)
            teamData = r.json()
            for player in teamData['teams'][0]['roster']['roster']:
                if player['position']['name'] == 'Goalie':
                    if 'jerseyNumber' in player.keys():
                        listGoalies.append((player['person']['id'],
                                            player['person']['fullName'],
                                            team['name'],
                                            player['jerseyNumber']))
                else:
                    if 'jerseyNumber' in player.keys():
                        listSkaters.append((player['person']['id'],
                                            player['person']['fullName'],
                                            team['name'],
                                            player['jerseyNumber'],
                                            player['position']['name']))

        # build dataframes for skaters and goalies
        dfGoalies = pd.DataFrame(columns=['id','name', 'teamName', 'evenSaves',
                                        'evenShots','evenStrengthSavePercentage',
                                        'games','gamesStarted','goalAgainstAverage',
                                        'goalsAgainst','losses','ot','powerPlaySavePercentage',
                                        'powerPlaySaves','powerPlayShots','savePercentage'
                                        'saves','shortHandedSavePercentage','shortHandedSaves'
                                        'shortHandedShots','shotsAgainst','shutouts'
                                        'ties','timeOnIce','timeOnIcePerGame'])

        for player in listGoalies:
            print(player[1])
            playerId = player[0]
            playerURL = 'https://statsapi.web.nhl.com/api/v1/people/' + str(playerId) + '/stats?stats=statsSingleSeason&season=20172018'
            r = self.getRequest(playerURL)
            playerData = r.json()
            if playerData['stats'][0]['splits']==[]:
                print("Empty")
                continue
            playerStats = playerData['stats'][0]['splits'][0]['stat']
            playerStats['id'] = playerId
            playerStats['name'] = player[1]
            playerStats['teamName'] = player[2]
            playerStats['jerseyNumber'] = player[3]
            tempDf = pd.DataFrame.from_records([playerStats])
            dfGoalies = dfGoalies.append(tempDf, ignore_index=True, sort = False)

        dfSkaters = pd.DataFrame(columns=['id','name','teamName',
                                        'position','blocked','evenTimeOnIce',
                                        'evenTimeOnIcePerGame','faceOffPct',
                                        'gameWinningGoals','games','goals','hits',
                                        'overTimeGoals','penaltyMinutes','pim',
                                        'plusMinus','points','powerPlayGoals',
                                        'powerPlayPoints','powerPlayTimeOnIce',
                                        'powerPlayTimeOnIcePerGame','shifts',
                                        'shortHandedGoals','shortHandedPoints'
                                        'shortHandedTimeOnIce','shortHandedTimeOnIcePerGame',
                                        'shotPct','shots','timeOnIce','timeOnIcePerGame'])

        for player in listSkaters:
            print(player[1])
            playerId = player[0]
            playerURL = 'https://statsapi.web.nhl.com/api/v1/people/' + str(playerId) + '/stats?stats=statsSingleSeason&season=20172018'
            r = self.getRequest(playerURL)
            playerData = r.json()
            if playerData['stats'][0]['splits']==[]:
                print("Empty")
                continue
            playerStats = playerData['stats'][0]['splits'][0]['stat']
            playerStats['id'] = playerId
            playerStats['name'] = player[1]
            playerStats['teamName'] = player[2]
            playerStats['jerseyNumber'] = player[3]
            playerStats['position'] = player[4]
            tempDf = pd.DataFrame.from_records([playerStats])
            dfSkaters = dfSkaters.append(tempDf, ignore_index=True, sort = False)

        # insert team data into the database
        for i in range(dfTeams.shape[0]):
            print(dfTeams.loc[i,'teamName'])
            goalsFor = int(round(dfTeams.loc[i,'gamesPlayed'] * dfTeams.loc[i, 'goalsPerGame']))
            goalsAgainst = int(round(dfTeams.loc[i,'gamesPlayed'] * dfTeams.loc[i, 'goalsAgainstPerGame']))

            if NhlTeam.objects.filter(team_name=dfTeams.loc[i, 'teamName']).exists():
                # update
                team = NhlTeam.objects.get(pk=dfTeams.loc[i, 'teamName'])
                team.goals_for = goalsFor
                team.goals_against = goalsAgainst
                team.wins = dfTeams.loc[i, 'wins']
                team.losses = dfTeams.loc[i, 'losses']
                team.overtime_losses = dfTeams.loc[i, 'ot']
                team.save()
            else:
                # add to the db
                NhlTeam.objects.create(team_name=dfTeams.loc[i, 'teamName'], goals_for=goalsFor,
                    goals_against=goalsAgainst, wins=dfTeams.loc[i, 'wins'], losses=dfTeams.loc[i, 'losses'],
                    overtime_losses=dfTeams.loc[i, 'ot'])

            print("Record inserted successfully into nhl_team table")

        # insert goalie data into the database
        for i in range(dfGoalies.shape[0]):
            print(dfGoalies.loc[i, 'name'])

            if NhlPlayers.objects.filter(id=dfGoalies.loc[i, 'id']).exists():
                # update
                print('this')
                player = NhlPlayers.objects.get(pk=dfGoalies.loc[i, 'id'])
                player.jersey_number = dfGoalies.loc[i, 'jerseyNumber']
                player.name = dfGoalies.loc[i, 'name']
                player.games_played = dfGoalies.loc[i, 'games']
                player.save()

                goalie = NhlGoalies.objects.get(pk=player)
                goalie.wins = dfGoalies.loc[i, 'wins']
                goalie.losses = dfGoalies.loc[i, 'losses']
                goalie.overtime_losses = dfGoalies.loc[i, 'ot']
                goalie.shots_against = dfGoalies.loc[i, 'shotsAgainst']
                goalie.saves = dfGoalies.loc[i, 'saves']
                goalie.shutouts = dfGoalies.loc[i, 'shutouts']
                goalie.save()
            else:
                # add to the db
                t = NhlTeam.objects.get(pk=dfGoalies.loc[i, 'teamName'])

                player = NhlPlayers.objects.create(id=dfGoalies.loc[i, 'id'], team_name=t,
                    jersey_number=dfGoalies.loc[i, 'jerseyNumber'], name=dfGoalies.loc[i, 'name'],
                    games_played=dfGoalies.loc[i, 'games'])

                NhlGoalies.objects.create(id=player, wins=dfGoalies.loc[i, 'wins'],
                    losses=dfGoalies.loc[i, 'losses'], overtime_losses=dfGoalies.loc[i, 'ot'],
                    shots_against=dfGoalies.loc[i, 'shotsAgainst'], saves=dfGoalies.loc[i, 'saves'],
                    shutouts=dfGoalies.loc[i, 'shutouts'])

            print("Record inserted successfully into nhl_goalies table")

        # insert skater data into the database
        for i in range(dfSkaters.shape[0]):
            print(dfSkaters.loc[i, 'name'])

            if 'Center' in dfSkaters.loc[i, 'position']:
                center = 1
                defence = 0
                left = 0
                right = 0
            elif 'Defense' in dfSkaters.loc[i, 'position']:
                center = 0
                defence = 1
                left = 0
                right = 0
            elif 'Left' in dfSkaters.loc[i, 'position']:
                center = 0
                defence = 0
                left = 1
                right = 0
            else:
                center = 0
                defence = 0
                left = 0
                right = 1

            if NhlPlayers.objects.filter(id=dfSkaters.loc[i, 'id']).exists():
                # update
                player = NhlPlayers.objects.get(pk=dfSkaters.loc[i, 'id'])
                player.jersey_number = dfSkaters.loc[i, 'jerseyNumber']
                player.name = dfSkaters.loc[i, 'name']
                player.games_played = dfSkaters.loc[i, 'games']
                player.save()

                skater = NhlSkaters.objects.get(pk=player)
                skater.goals = dfSkaters.loc[i, 'goals']
                skater.assists = dfSkaters.loc[i, 'assists']
                skater.powerplay_goals = dfSkaters.loc[i, 'powerPlayGoals']
                skater.shorthanded_goals = dfSkaters.loc[i, 'shortHandedGoals']
                skater.plus_minus = dfSkaters.loc[i, 'plusMinus']
                skater.penalty_minutes = dfSkaters.loc[i, 'penaltyMinutes']
                skater.game_winning_goals = dfSkaters.loc[i, 'gameWinningGoals']
                skater.shots_on_goal = dfSkaters.loc[i, 'shots']
                skater.center_flag = center
                skater.left_wing_flag = left
                skater.right_wing_flag = right
                skater.defencemen_flag = defence
                skater.save()
            else:
                # add to the db
                t = NhlTeam.objects.get(pk=dfSkaters.loc[i, 'teamName'])

                player = NhlPlayers.objects.create(id=dfSkaters.loc[i, 'id'], team_name=t,
                    jersey_number=dfSkaters.loc[i, 'jerseyNumber'], name=dfSkaters.loc[i, 'name'],
                    games_played=dfSkaters.loc[i, 'games'])

                NhlSkaters.objects.create(id=player, goals=dfSkaters.loc[i, 'goals'],
                    assists=dfSkaters.loc[i, 'assists'], powerplay_goals=dfSkaters.loc[i, 'powerPlayGoals'],
                    shorthanded_goals=dfSkaters.loc[i, 'shortHandedGoals'],
                    shorthanded_points=dfSkaters.loc[i, 'shortHandedPoints'], plus_minus=dfSkaters.loc[i, 'plusMinus'],
                    penalty_minutes=dfSkaters.loc[i, 'penaltyMinutes'],
                    game_winning_goals=dfSkaters.loc[i, 'gameWinningGoals'], shots_on_goal=dfSkaters.loc[i, 'shots'],
                    center_flag=center, right_wing_flag=right, left_wing_flag=left, defencemen_flag=defence)

            print("Record inserted successfully into nhl_skaters table")
