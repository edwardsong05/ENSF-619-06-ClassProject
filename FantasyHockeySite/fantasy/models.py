from django.db import models

# Create your models here.
class NhlTeam(models.Model):
    team_name = models.CharField(db_column='Team_Name', primary_key=True, max_length=45)
    goals_for = models.IntegerField(db_column='Goals_For')
    goals_against = models.IntegerField(db_column='Goals_Against')
    wins = models.IntegerField(db_column='Wins')
    losses = models.IntegerField(db_column='Losses')
    overtime_losses = models.IntegerField(db_column='Overtime_Losses')

    class Meta:
        db_table = 'nhl_team'


class NhlPlayers(models.Model):
    jersey_number = models.IntegerField(db_column='Jersey_Number', primary_key=True)
    team_name = models.ForeignKey('NhlTeam', models.CASCADE, db_column='Team_Name')
    name = models.CharField(db_column='Name', max_length=45)
    games_played = models.IntegerField(db_column='Games_Played')

    class Meta:
        db_table = 'nhl_players'
        unique_together = (('jersey_number', 'team_name'),)


class NhlSkaters(models.Model):
    jersey_number = models.ForeignKey(NhlPlayers, models.CASCADE, related_name='NhlSkaters_Jersey_Number', db_column='Jersey_Number', primary_key=True)
    team_name = models.ForeignKey(NhlPlayers, models.CASCADE, related_name='NhlSkaters_Team_Name', db_column='Team_Name')
    goals = models.IntegerField(db_column='Goals')
    powerplay_goals = models.IntegerField(db_column='Powerplay_Goals')
    powerplay_points = models.IntegerField(db_column='Powerplay_Points')
    shorthanded_goals = models.IntegerField(db_column='Shorthanded_Goals')
    shorthanded_points = models.IntegerField(db_column='Shorthanded_Points')
    plus_minus = models.IntegerField(db_column='+/-')  # Field renamed to remove unsuitable characters.
    penalty_minutes = models.IntegerField(db_column='Penalty_Minutes')
    game_winning_goals = models.IntegerField(db_column='Game_Winning_Goals')
    shots_on_goal = models.IntegerField(db_column='Shots_on_Goal')
    center_flag = models.IntegerField(db_column='Center_Flag')
    left_wing_flag = models.IntegerField(db_column='Left_Wing_Flag')
    right_wing_flag = models.IntegerField(db_column='Right_Wing_Flag')
    defencemen_flag = models.CharField(db_column='Defencemen_Flag', max_length=45)

    class Meta:
        db_table = 'nhl_skaters'
        unique_together = (('jersey_number', 'team_name'),)


class NhlGoalies(models.Model):
    jersey_number = models.ForeignKey('NhlPlayers', models.CASCADE, related_name='NhlGoalies_Jersey_Number', db_column='Jersey_Number', primary_key=True)
    team_name = models.ForeignKey('NhlPlayers', models.CASCADE, related_name='NhlGoalies_Team_Name', db_column='Team_Name')
    wins = models.IntegerField(db_column='Wins')
    losses = models.IntegerField(db_column='Losses')
    overtime_losses = models.IntegerField(db_column='Overtime_Losses')
    shots_against = models.IntegerField(db_column='Shots_Against')
    saves = models.IntegerField(db_column='Saves')
    shutouts = models.IntegerField(db_column='Shutouts')

    class Meta:
        db_table = 'nhl_goalies'
        unique_together = (('jersey_number', 'team_name'),)


class Owner(models.Model):
    username = models.CharField(db_column='Username', primary_key=True, max_length=45)
    name = models.CharField(db_column='Name', max_length=45)
    password = models.CharField(db_column='Password', max_length=45)

    class Meta:
        db_table = 'owner'


class LeagueCommisioner(models.Model):
    username = models.ForeignKey('Owner', models.CASCADE, db_column='Username', primary_key=True)

    class Meta:
        db_table = 'league_commisioner'


class FantasyLeague(models.Model):
    fantasy_league_name = models.CharField(db_column='Fantasy_League_Name', primary_key=True, max_length=45)
    goals_weight = models.DecimalField(db_column='Goals_Weight', max_digits=10, decimal_places=0)
    assists_weight = models.DecimalField(db_column='Assists_Weight', max_digits=10, decimal_places=0)
    powerplay_goals_weight = models.DecimalField(db_column='Powerplay_Goals_Weight', max_digits=10, decimal_places=0)
    shorthanded_goals_weight = models.DecimalField(db_column='Shorthanded_Goals_Weight', max_digits=10, decimal_places=0)
    shorthanded_assists_weight = models.DecimalField(db_column='Shorthanded_Assists_Weight', max_digits=10, decimal_places=0)
    plus_minus = models.DecimalField(db_column='+/-_Weight', max_digits=10, decimal_places=0)  # Field renamed to remove unsuitable characters.
    penalty_minutes_weight = models.DecimalField(db_column='Penalty_Minutes_Weight', max_digits=10, decimal_places=0)
    game_winning_goals_weight = models.DecimalField(db_column='Game_Winning_Goals_Weight', max_digits=10, decimal_places=0)
    shots_on_goal_weight = models.DecimalField(db_column='Shots_on_Goal_Weight', max_digits=10, decimal_places=0)
    wins_weight = models.DecimalField(db_column='Wins_Weight', max_digits=10, decimal_places=0)
    losses_weight = models.DecimalField(db_column='Losses_Weight', max_digits=10, decimal_places=0)
    overtime_losses_weight = models.DecimalField(db_column='Overtime_Losses_Weight', max_digits=10, decimal_places=0)
    saves_weight = models.DecimalField(db_column='Saves_Weight', max_digits=10, decimal_places=0)
    goals_against_weight = models.DecimalField(db_column='Goals_Against_Weight', max_digits=10, decimal_places=0)
    saves_percentage_weight = models.DecimalField(db_column='Saves_Percentage_Weight', max_digits=10, decimal_places=0)
    goals_against_average_weight = models.DecimalField(db_column='Goals_Against_Average_Weight', max_digits=10, decimal_places=0)
    shutouts_weight = models.DecimalField(db_column='Shutouts_Weight', max_digits=10, decimal_places=0)
    maximum_number_of_players = models.IntegerField(db_column='Maximum_Number_of_Players')
    minimum_number_of_goalies = models.IntegerField(db_column='Minimum_Number_of_Goalies')
    minimum_number_of_defencemen = models.IntegerField(db_column='Minimum_Number_of_Defencemen')
    minimum_number_of_right_wing = models.IntegerField(db_column='Minimum_Number_of_Right_Wing')
    minimum_number_of_left_wing = models.IntegerField(db_column='Minimum_Number_of_Left_Wing')
    minimum_number_of_center = models.IntegerField(db_column='Minimum_Number_of_Center')
    fantasy_league_invite_code = models.CharField(db_column='Fantasy_League_Invite_Code', max_length=45)
    username = models.ForeignKey('LeagueCommisioner', models.CASCADE, db_column='Username')

    class Meta:
        db_table = 'fantasy_league'


class Participates(models.Model):
    username = models.ForeignKey(Owner, models.CASCADE, db_column='Username', primary_key=True)
    fantasy_league_name = models.ForeignKey(FantasyLeague, models.CASCADE, db_column='Fantasy_League_Name')

    class Meta:
        db_table = 'participates'
        unique_together = (('username', 'fantasy_league_name'),)


class FantasyTeam(models.Model):
    fantasy_team_name = models.CharField(db_column='Fantasy_Team_Name', primary_key=True, max_length=45)
    fantasy_league_name = models.ForeignKey(FantasyLeague, models.CASCADE, db_column='Fantasy_League_Name')
    fantasy_points = models.IntegerField(db_column='Fantasy_Points')
    username = models.ForeignKey('Owner', models.CASCADE, db_column='Username')

    class Meta:
        db_table = 'fantasy_team'
        unique_together = (('fantasy_team_name', 'fantasy_league_name'),)


class GoalieTeams(models.Model):
    fantasy_team_name = models.ForeignKey(FantasyTeam, models.CASCADE, related_name='Goalies_Fantasy_Team_Name', db_column='Fantasy_Team_Name', primary_key=True)
    fantasy_league_name = models.ForeignKey(FantasyTeam, models.CASCADE, related_name='Goalies_Fantasy_League_Name', db_column='Fantasy_League_Name')
    jersey_number = models.ForeignKey('NhlGoalies', models.CASCADE, related_name='Goalies_Jersey_Number', db_column='Jersey_Number')
    team_name = models.ForeignKey('NhlGoalies', models.CASCADE, related_name='Goalies_Team_Name', db_column='Team_Name')

    class Meta:
        db_table = 'goalie_teams'
        unique_together = (('fantasy_team_name', 'fantasy_league_name', 'jersey_number', 'team_name'),)


class SkaterTeams(models.Model):
    fantasy_team_name = models.ForeignKey(FantasyTeam, models.CASCADE, related_name='SkaterTeams_Fantasy_Team_Name', db_column='Fantasy_Team_Name', primary_key=True)
    fantasy_league_name = models.ForeignKey(FantasyTeam, models.CASCADE, related_name='SkaterTeams_Fantasy_League_Name', db_column='Fantasy_League_Name')
    jersey_number = models.ForeignKey(NhlSkaters, models.CASCADE, related_name='SkaterTeams_Jersey_Number', db_column='Jersey_Number')
    team_name = models.ForeignKey(NhlSkaters, models.CASCADE, related_name='SkaterTeams_Team_Name', db_column='Team_Name')

    class Meta:
        db_table = 'skater_teams'
        unique_together = (('fantasy_team_name', 'fantasy_league_name', 'jersey_number', 'team_name'),)
