from django.db import models


# Create your models here.
class NhlTeam(models.Model):
    team_name = models.CharField(db_column='Team_Name', primary_key=True, max_length=45)
    goals_for = models.IntegerField(db_column='Goals_For', null=False, default=0)
    goals_against = models.IntegerField(db_column='Goals_Against', null=False, default=0)
    wins = models.IntegerField(db_column='Wins', null=False, default=0)
    losses = models.IntegerField(db_column='Losses', null=False, default=0)
    overtime_losses = models.IntegerField(db_column='Overtime_Losses', null=False, default=0)

    class Meta:
        db_table = 'nhl_team'


class NhlPlayers(models.Model):
    id = models.IntegerField(db_column='ID', primary_key=True)
    jersey_number = models.IntegerField(db_column='Jersey_Number', null=False)
    team_name = models.ForeignKey('NhlTeam', models.CASCADE, db_column='Team_Name', null=False)
    name = models.CharField(db_column='Name', max_length=45, null=False)
    games_played = models.IntegerField(db_column='Games_Played', null=False, default=0)

    class Meta:
        db_table = 'nhl_players'
        unique_together = (('jersey_number', 'team_name'),)


class NhlSkaters(models.Model):
    jersey_number = models.ForeignKey(NhlPlayers, models.CASCADE, related_name='NhlSkaters_Jersey_Number', db_column='Jersey_Number', primary_key=True)
    team_name = models.ForeignKey(NhlPlayers, models.CASCADE, related_name='NhlSkaters_Team_Name', db_column='Team_Name', null=False)
    goals = models.IntegerField(db_column='Goals', null=False, default=0)
    powerplay_goals = models.IntegerField(db_column='Powerplay_Goals', null=False, default=0)
    powerplay_points = models.IntegerField(db_column='Powerplay_Points', null=False, default=0)
    shorthanded_goals = models.IntegerField(db_column='Shorthanded_Goals', null=False, default=0)
    shorthanded_points = models.IntegerField(db_column='Shorthanded_Points', null=False, default=0)
    plus_minus = models.IntegerField(db_column='+/-', null=False, default=0)  # Field renamed to remove unsuitable characters.
    penalty_minutes = models.IntegerField(db_column='Penalty_Minutes', null=False, default=0)
    game_winning_goals = models.IntegerField(db_column='Game_Winning_Goals', null=False, default=0)
    shots_on_goal = models.IntegerField(db_column='Shots_on_Goal', null=False, default=0)
    center_flag = models.IntegerField(db_column='Center_Flag', null=False)
    left_wing_flag = models.IntegerField(db_column='Left_Wing_Flag', null=False)
    right_wing_flag = models.IntegerField(db_column='Right_Wing_Flag', null=False)
    defencemen_flag = models.IntegerField(db_column='Defencemen_Flag', null=False)

    class Meta:
        db_table = 'nhl_skaters'
        unique_together = (('jersey_number', 'team_name'),)


class NhlGoalies(models.Model):
    jersey_number = models.ForeignKey('NhlPlayers', models.CASCADE, related_name='NhlGoalies_Jersey_Number', db_column='Jersey_Number', primary_key=True)
    team_name = models.ForeignKey('NhlPlayers', models.CASCADE, related_name='NhlGoalies_Team_Name', db_column='Team_Name', null=False)
    wins = models.IntegerField(db_column='Wins', null=False, default=0)
    losses = models.IntegerField(db_column='Losses', null=False, default=0)
    overtime_losses = models.IntegerField(db_column='Overtime_Losses', null=False, default=0)
    shots_against = models.IntegerField(db_column='Shots_Against', null=False, default=0)
    saves = models.IntegerField(db_column='Saves', null=False, default=0)
    shutouts = models.IntegerField(db_column='Shutouts', null=False, default=0)

    class Meta:
        db_table = 'nhl_goalies'
        unique_together = (('jersey_number', 'team_name'),)


class Owner(models.Model):
    username = models.CharField(db_column='Username', primary_key=True, max_length=45, null=False)
    name = models.CharField(db_column='Name', max_length=45, null=False)
    password = models.CharField(db_column='Password', max_length=45, null=False)

    class Meta:
        db_table = 'owner'


class LeagueCommisioner(models.Model):
    username = models.ForeignKey('Owner', models.CASCADE, db_column='Username', primary_key=True)

    class Meta:
        db_table = 'league_commisioner'


class FantasyLeague(models.Model):
    fantasy_league_name = models.CharField(db_column='Fantasy_League_Name', primary_key=True, max_length=45)
    goals_weight = models.DecimalField(db_column='Goals_Weight', max_digits=10, decimal_places=1, null=False, default=3)
    assists_weight = models.DecimalField(db_column='Assists_Weight', max_digits=10, decimal_places=1, null=False, default=2)
    powerplay_goals_weight = models.DecimalField(db_column='Powerplay_Goals_Weight', max_digits=10, decimal_places=1, null=False, default=1)
    shorthanded_goals_weight = models.DecimalField(db_column='Shorthanded_Goals_Weight', max_digits=10, decimal_places=1, null=False, default=2)
    shorthanded_assists_weight = models.DecimalField(db_column='Shorthanded_Assists_Weight', max_digits=10, decimal_places=1, null=False, default=1)
    plus_minus = models.DecimalField(db_column='+/-_Weight', max_digits=10, decimal_places=1, null=False, default=1)  # Field renamed to remove unsuitable characters.
    penalty_minutes_weight = models.DecimalField(db_column='Penalty_Minutes_Weight', max_digits=10, decimal_places=1, null=False, default=0.5)
    game_winning_goals_weight = models.DecimalField(db_column='Game_Winning_Goals_Weight', max_digits=10, decimal_places=1, null=False, default=1)
    shots_on_goal_weight = models.DecimalField(db_column='Shots_on_Goal_Weight', max_digits=10, decimal_places=1, null=False, default=0.4)
    wins_weight = models.DecimalField(db_column='Wins_Weight', max_digits=10, decimal_places=1, null=False, default=4)
    losses_weight = models.DecimalField(db_column='Losses_Weight', max_digits=10, decimal_places=1, null=False, default=-2)
    overtime_losses_weight = models.DecimalField(db_column='Overtime_Losses_Weight', max_digits=10, decimal_places=1, null=False, default=-2)
    saves_weight = models.DecimalField(db_column='Saves_Weight', max_digits=10, decimal_places=1, null=False, default=0.2)
    goals_against_weight = models.DecimalField(db_column='Goals_Against_Weight', max_digits=10, decimal_places=1, null=False, default=-1)
    saves_percentage_weight = models.DecimalField(db_column='Saves_Percentage_Weight', max_digits=10, decimal_places=1, null=False, default=0)
    goals_against_average_weight = models.DecimalField(db_column='Goals_Against_Average_Weight', max_digits=10, decimal_places=1, null=False, default=0)
    shutouts_weight = models.DecimalField(db_column='Shutouts_Weight', max_digits=10, decimal_places=1, null=False, default=2)
    maximum_number_of_players = models.IntegerField(db_column='Maximum_Number_of_Players', null=False, default=20)
    minimum_number_of_goalies = models.IntegerField(db_column='Minimum_Number_of_Goalies', null=False, default=1)
    minimum_number_of_defencemen = models.IntegerField(db_column='Minimum_Number_of_Defencemen', null=False, default=2)
    minimum_number_of_right_wing = models.IntegerField(db_column='Minimum_Number_of_Right_Wing', null=False, default=1)
    minimum_number_of_left_wing = models.IntegerField(db_column='Minimum_Number_of_Left_Wing', null=False, default=1)
    minimum_number_of_center = models.IntegerField(db_column='Minimum_Number_of_Center', null=False, default=1)
    fantasy_league_invite_code = models.CharField(db_column='Fantasy_League_Invite_Code', max_length=45, null=False)
    username = models.ForeignKey('LeagueCommisioner', models.CASCADE, db_column='Username')

    class Meta:
        db_table = 'fantasy_league'


class Participates(models.Model):
    username = models.ForeignKey(Owner, models.CASCADE, db_column='Username', primary_key=True)
    fantasy_league_name = models.ForeignKey(FantasyLeague, models.CASCADE, db_column='Fantasy_League_Name', null=False)

    class Meta:
        db_table = 'participates'
        unique_together = (('username', 'fantasy_league_name'),)


class FantasyTeam(models.Model):
    fantasy_team_name = models.CharField(db_column='Fantasy_Team_Name', primary_key=True, max_length=45)
    fantasy_league_name = models.ForeignKey(FantasyLeague, models.CASCADE, db_column='Fantasy_League_Name', null=False)
    fantasy_points = models.IntegerField(db_column='Fantasy_Points', null=False, default=0)
    username = models.ForeignKey('Owner', models.CASCADE, db_column='Username', null=False)

    class Meta:
        db_table = 'fantasy_team'
        unique_together = (('fantasy_team_name', 'fantasy_league_name'),)


class GoalieTeams(models.Model):
    fantasy_team_name = models.ForeignKey(FantasyTeam, models.CASCADE, related_name='Goalies_Fantasy_Team_Name', db_column='Fantasy_Team_Name', primary_key=True)
    fantasy_league_name = models.ForeignKey(FantasyTeam, models.CASCADE, related_name='Goalies_Fantasy_League_Name', db_column='Fantasy_League_Name', null=False)
    jersey_number = models.ForeignKey('NhlGoalies', models.CASCADE, related_name='Goalies_Jersey_Number', db_column='Jersey_Number', null=False)
    team_name = models.ForeignKey('NhlGoalies', models.CASCADE, related_name='Goalies_Team_Name', db_column='Team_Name', null=False)

    class Meta:
        db_table = 'goalie_teams'
        unique_together = (('fantasy_team_name', 'fantasy_league_name', 'jersey_number', 'team_name'),)


class SkaterTeams(models.Model):
    fantasy_team_name = models.ForeignKey(FantasyTeam, models.CASCADE, related_name='SkaterTeams_Fantasy_Team_Name', db_column='Fantasy_Team_Name', primary_key=True)
    fantasy_league_name = models.ForeignKey(FantasyTeam, models.CASCADE, related_name='SkaterTeams_Fantasy_League_Name', db_column='Fantasy_League_Name', null=False)
    jersey_number = models.ForeignKey(NhlSkaters, models.CASCADE, related_name='SkaterTeams_Jersey_Number', db_column='Jersey_Number', null=False)
    team_name = models.ForeignKey(NhlSkaters, models.CASCADE, related_name='SkaterTeams_Team_Name', db_column='Team_Name', null=False)

    class Meta:
        db_table = 'skater_teams'
        unique_together = (('fantasy_team_name', 'fantasy_league_name', 'jersey_number', 'team_name'),)
