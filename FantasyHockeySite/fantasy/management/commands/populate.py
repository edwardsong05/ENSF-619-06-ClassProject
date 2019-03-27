from django.core.management.base import BaseCommand, CommandError
from fantasy.models import NhlTeam
import requests
import pandas as pd
import pymysql


class Command(BaseCommand):
    help = 'Updates models in the NHL Team table'

    def handle(self, *args, ** options):
        # database connection params
        host_name = 'localhost'
        port_num = 3306
        user_name = 'root'
        psw = 'Password'
        db_name = 'fantasydb'

        baseURL = "https://statsapi.web.nhl.com"
        teamsURL = "https://statsapi.web.nhl.com/api/v1/teams"

        r = requests.get(teamsURL)
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
        for team in teamsData['teams']:
            teamURL = team['link']
            r = requests.get(baseURL + teamURL + "?expand=team.stats")
            print(team['name'], r.status_code)
            teamData = r.json()
            teamStats = teamData['teams'][0]['teamStats'][0]['splits'][0]['stat']
            teamStats['teamName'] = team['name']
            tempDf = pd.DataFrame.from_records([teamStats])
            dfTeams = dfTeams.append(tempDf, ignore_index=True)

        # get player ids and names and position
        listGoalies = []
        listSkaters = []

        #a = [teamsData['teams'][0]]
        #for team in a:
        for team in teamsData['teams']:
            teamURL = team['link']
            r = requests.get(baseURL + teamURL + "?expand=team.roster")
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

        ##build dataframes for skaters and goalies
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
            r = requests.get(playerURL)
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
            dfGoalies = dfGoalies.append(tempDf, ignore_index=True)

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
            r = requests.get(playerURL)
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
            dfSkaters = dfSkaters.append(tempDf, ignore_index=True)

        # insert team data into the database
        try:
            connection = pymysql.connect(host=host_name, port=port_num, user=user_name, passwd=psw, db=db_name)
            for i in range(dfTeams.shape[0]):
                print(dfTeams.loc[i,'teamName'])
                sql = \
                """INSERT INTO `nhl_team` (`team_name`, `goals_for`, `goals_against`, \
                    `wins`, `losses`, `overtime_losses`) VALUES (%s, %s, %s, %s, %s, %s) \
                    ON DUPLICATE KEY UPDATE \
                    team_name=VALUES(team_name), \
                    goals_for=VALUES(goals_for), \
                    goals_against=VALUES(goals_against), \
                    wins=VALUES(wins), \
                    losses=VALUES(losses), \
                    overtime_losses=VALUES(overtime_losses)"""
                with connection.cursor() as cursor:
                    goalsFor = int(round(dfTeams.loc[i,'gamesPlayed'] * dfTeams.loc[i,'goalsPerGame']))
                    goalsAgainst = int(round(dfTeams.loc[i,'gamesPlayed'] * dfTeams.loc[i,'goalsAgainstPerGame']))
                    cursor.execute(sql, (dfTeams.loc[i,'teamName'],
                                        str(goalsFor),
                                        str(goalsAgainst),
                                        str(dfTeams.loc[i,'wins']),
                                        str(dfTeams.loc[i,'losses']),
                                        str(dfTeams.loc[i,'ot'])))
                connection.commit()
                print ("Record inserted successfully into nhl_team table")
        except pymysql.Error as error:
            code, message = error.args
            print(">>>>>>>>>>>>>", code, message)
        finally:
            connection.close()

        # insert goalie data into the database
        try:
            connection = pymysql.connect(host=host_name, port=port_num, user=user_name, passwd=psw, db=db_name)
            for i in range(dfGoalies.shape[0]):
                print(dfGoalies.loc[i, 'name'])
                sql = \
                """INSERT INTO `nhl_players` (`id`, `jersey_number`, `team_name`, `name`, \
                    `games_played`) VALUES (%s, %s, %s, %s, %s) \
                    ON DUPLICATE KEY UPDATE \
                    id = VALUES(id), \
                    jersey_number=VALUES(jersey_number), \
                    team_name=VALUES(team_name), \
                    name=VALUES(name), \
                    games_played=VALUES(games_played)"""
                with connection.cursor() as cursor:
                    cursor.execute(sql, (str(dfGoalies.loc[i, 'id']),
                                        str(dfGoalies.loc[i, 'jerseyNumber']),
                                        dfGoalies.loc[i, 'teamName'],
                                        dfGoalies.loc[i, 'name'],
                                        str(dfGoalies.loc[i, 'games'])))
                connection.commit()

                sql = \
                """INSERT INTO `nhl_goalies` (`id`, `wins`, `losses`, `overtime_losses`, `shots_against`, `saves`, \
                    `shutouts`) VALUES (%s, %s, %s, %s, %s, %s, %s) \
                    ON DUPLICATE KEY UPDATE \
                    id = VALUES(id), \
                    wins=VALUES(wins), \
                    losses=VALUES(losses), \
                    overtime_losses=VALUES(overtime_losses), \
                    shots_against=VALUES(shots_against), \
                    saves=VALUES(saves), \
                    shutouts=VALUES(shutouts)"""
                with connection.cursor() as cursor:
                    cursor.execute(sql, (str(dfGoalies.loc[i, 'id']),
                                        str(dfGoalies.loc[i, 'wins']),
                                        str(dfGoalies.loc[i, 'losses']),
                                        str(dfGoalies.loc[i, 'ot']),
                                        str(dfGoalies.loc[i, 'shotsAgainst']),
                                        str(dfGoalies.loc[i, 'saves']),
                                        str(dfGoalies.loc[i, 'shutouts'])))
                connection.commit()
                print ("Record inserted successfully into nhl_goalies table")
        except pymysql.Error as error:
            code, message = error.args
            print(">>>>>>>>>>>>>", code, message)
        finally:
            connection.close()

        # insert skater data into the database
        try:
            connection = pymysql.connect(host=host_name, port=port_num, user=user_name, passwd=psw, db=db_name)
            for i in range(dfSkaters.shape[0]):
                print(dfSkaters.loc[i, 'name'])
                sql = \
                """INSERT INTO `nhl_players` (`id`, `jersey_number`, `team_name`, `name`, \
                    `games_played`) VALUES (%s, %s, %s, %s, %s) \
                    ON DUPLICATE KEY UPDATE \
                    id = VALUES(id), \
                    jersey_number=VALUES(jersey_number), \
                    team_name=VALUES(team_name), \
                    name=VALUES(name), \
                    games_played=VALUES(games_played)"""
                with connection.cursor() as cursor:
                    cursor.execute(sql, (str(dfSkaters.loc[i, 'id']),
                                        str(dfSkaters.loc[i, 'jerseyNumber']),
                                        dfSkaters.loc[i, 'teamName'],
                                        dfSkaters.loc[i, 'name'],
                                        str(dfSkaters.loc[i, 'games'])))
                connection.commit()

                sql = \
                """INSERT INTO `nhl_skaters` (`id`, `goals`, `powerplay_goals`, `powerplay_points`, `shorthanded_goals`, \
                    `shorthanded_points`, `plus_minus`, `penalty_minutes`, `game_winning_goals`, `shots_on_goal`, \
                    `center_flag`, `left_wing_flag`, `right_wing_flag`, `defencemen_flag`) \
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) \
                    ON DUPLICATE KEY UPDATE \
                    id = VALUES(id), \
                    goals=VALUES(goals), \
                    powerplay_goals=VALUES(powerplay_goals), \
                    powerplay_points=VALUES(powerplay_points), \
                    shorthanded_goals=VALUES(shorthanded_goals), \
                    shorthanded_points=VALUES(shorthanded_points), \
                    plus_minus=VALUES(plus_minus), \
                    penalty_minutes=VALUES(penalty_minutes), \
                    game_winning_goals=VALUES(game_winning_goals), \
                    shots_on_goal=VALUES(shots_on_goal), \
                    center_flag=VALUES(center_flag), \
                    left_wing_flag=VALUES(left_wing_flag), \
                    right_wing_flag=VALUES(right_wing_flag), \
                    defencemen_flag=VALUES(defencemen_flag)"""
                with connection.cursor() as cursor:
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
                    cursor.execute(sql, (str(dfSkaters.loc[i, 'id']),
                                        str(dfSkaters.loc[i, 'goals']),
                                        str(dfSkaters.loc[i, 'powerPlayGoals']),
                                        str(dfSkaters.loc[i, 'powerPlayPoints']),
                                        str(dfSkaters.loc[i, 'shortHandedGoals']),
                                        str(dfSkaters.loc[i, 'shortHandedPoints']),
                                        str(dfSkaters.loc[i, 'plusMinus']),
                                        str(dfSkaters.loc[i, 'penaltyMinutes']),
                                        str(dfSkaters.loc[i, 'gameWinningGoals']),
                                        str(dfSkaters.loc[i, 'shots']),
                                        str(center),
                                        str(defence),
                                        str(left),
                                        str(right)))
                connection.commit()
                print ("Record inserted successfully into nhl_skaters table")
        except pymysql.Error as error:
            code, message = error.args
            print(">>>>>>>>>>>>>", code, message)
        finally:
            connection.close()

# Center, Defensemen, Left Wing, Right Wing
