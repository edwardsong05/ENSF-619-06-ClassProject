# -*- coding: utf-8 -*-

#%%
import requests
import pandas as pd
import pymysql
#%%
baseURL = "https://statsapi.web.nhl.com"
teamsURL = "https://statsapi.web.nhl.com/api/v1/teams"

r = requests.get(teamsURL)
teamsData = r.json()

#%%
##get team stats
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
    rosterURL = teamURL + '/roster'

#%%
rosterURL = baseURL + teamURL + '/roster'
r = requests.get(rosterURL)
print(team['name'], r.status_code)
teamData = r.json()
#%%
##get player ids and names and position
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

#%%
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
#%%
##Insert team data into the database
try:
    connection = pymysql.connect(host='localhost', port=3306, user='fantasyserver', passwd='fantasypass', db='fantasydb')
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
        print ("Record inserted successfully into python_users table")
except pymysql.Error as error:
        code, message = error.args
        print(">>>>>>>>>>>>>", code, message)
finally:
    connection.close()