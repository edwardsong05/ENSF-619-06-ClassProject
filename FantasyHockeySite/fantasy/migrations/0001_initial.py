# Generated by Django 2.1.7 on 2019-03-30 20:20

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='FantasyLeague',
            fields=[
                ('fantasy_league_name', models.CharField(db_column='Fantasy_League_Name', max_length=45, primary_key=True, serialize=False)),
                ('goals_weight', models.DecimalField(db_column='Goals_Weight', decimal_places=1, default=3, max_digits=10)),
                ('assists_weight', models.DecimalField(db_column='Assists_Weight', decimal_places=1, default=2, max_digits=10)),
                ('powerplay_goals_weight', models.DecimalField(db_column='Powerplay_Goals_Weight', decimal_places=1, default=1, max_digits=10)),
                ('powerplay_points_weight', models.DecimalField(db_column='Powerplay_Points_Weight', decimal_places=1, default=1, max_digits=10)),
                ('shorthanded_goals_weight', models.DecimalField(db_column='Shorthanded_Goals_Weight', decimal_places=1, default=2, max_digits=10)),
                ('shorthanded_points_weight', models.DecimalField(db_column='Shorthanded_Points_Weight', decimal_places=1, default=1, max_digits=10)),
                ('plus_minus_weight', models.DecimalField(db_column='+/-_Weight', decimal_places=1, default=1, max_digits=10)),
                ('penalty_minutes_weight', models.DecimalField(db_column='Penalty_Minutes_Weight', decimal_places=1, default=0.5, max_digits=10)),
                ('game_winning_goals_weight', models.DecimalField(db_column='Game_Winning_Goals_Weight', decimal_places=1, default=1, max_digits=10)),
                ('shots_on_goal_weight', models.DecimalField(db_column='Shots_on_Goal_Weight', decimal_places=1, default=0.4, max_digits=10)),
                ('wins_weight', models.DecimalField(db_column='Wins_Weight', decimal_places=1, default=4, max_digits=10)),
                ('losses_weight', models.DecimalField(db_column='Losses_Weight', decimal_places=1, default=-2, max_digits=10)),
                ('overtime_losses_weight', models.DecimalField(db_column='Overtime_Losses_Weight', decimal_places=1, default=-2, max_digits=10)),
                ('shots_against_weight', models.DecimalField(db_column='Shots_Against_Weight', decimal_places=1, default=0.2, max_digits=10)),
                ('saves_weight', models.DecimalField(db_column='Saves_Weight', decimal_places=1, default=0.2, max_digits=10)),
                ('goals_against_weight', models.DecimalField(db_column='Goals_Against_Weight', decimal_places=1, default=-1, max_digits=10)),
                ('saves_percentage_weight', models.DecimalField(db_column='Saves_Percentage_Weight', decimal_places=1, default=0, max_digits=10)),
                ('goals_against_average_weight', models.DecimalField(db_column='Goals_Against_Average_Weight', decimal_places=1, default=0, max_digits=10)),
                ('shutouts_weight', models.DecimalField(db_column='Shutouts_Weight', decimal_places=1, default=2, max_digits=10)),
                ('maximum_number_of_players', models.IntegerField(db_column='Maximum_Number_of_Players', default=20)),
                ('minimum_number_of_goalies', models.IntegerField(db_column='Minimum_Number_of_Goalies', default=1)),
                ('minimum_number_of_defencemen', models.IntegerField(db_column='Minimum_Number_of_Defencemen', default=2)),
                ('minimum_number_of_right_wing', models.IntegerField(db_column='Minimum_Number_of_Right_Wing', default=1)),
                ('minimum_number_of_left_wing', models.IntegerField(db_column='Minimum_Number_of_Left_Wing', default=1)),
                ('minimum_number_of_center', models.IntegerField(db_column='Minimum_Number_of_Center', default=1)),
                ('fantasy_league_invite_code', models.CharField(db_column='Fantasy_League_Invite_Code', max_length=45, unique=True)),
            ],
            options={
                'db_table': 'fantasy_league',
            },
        ),
        migrations.CreateModel(
            name='FantasyTeam',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fantasy_team_name', models.CharField(db_column='Fantasy_Team_Name', max_length=45)),
                ('fantasy_points', models.IntegerField(db_column='Fantasy_Points', default=0)),
                ('fantasy_league_name', models.ForeignKey(db_column='Fantasy_League_Name', on_delete=django.db.models.deletion.CASCADE, to='fantasy.FantasyLeague')),
            ],
            options={
                'db_table': 'fantasy_team',
            },
        ),
        migrations.CreateModel(
            name='GoalieTeams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fantasy_league_name', models.ForeignKey(db_column='Fantasy_League_Name', on_delete=django.db.models.deletion.CASCADE, related_name='Goalies_Fantasy_League_Name', to='fantasy.FantasyLeague')),
            ],
            options={
                'db_table': 'goalie_teams',
            },
        ),
        migrations.CreateModel(
            name='LeagueCommissioner',
            fields=[
                ('userid', models.ForeignKey(db_column='User_ID', on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'league_commissioner',
            },
        ),
        migrations.CreateModel(
            name='NhlPlayers',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('jersey_number', models.IntegerField(db_column='Jersey_Number')),
                ('name', models.CharField(db_column='Name', max_length=45)),
                ('games_played', models.IntegerField(db_column='Games_Played', default=0)),
            ],
            options={
                'db_table': 'nhl_players',
            },
        ),
        migrations.CreateModel(
            name='NhlTeam',
            fields=[
                ('team_name', models.CharField(db_column='Team_Name', max_length=45, primary_key=True, serialize=False)),
                ('goals_for', models.IntegerField(db_column='Goals_For', default=0)),
                ('goals_against', models.IntegerField(db_column='Goals_Against', default=0)),
                ('wins', models.IntegerField(db_column='Wins', default=0)),
                ('losses', models.IntegerField(db_column='Losses', default=0)),
                ('overtime_losses', models.IntegerField(db_column='Overtime_Losses', default=0)),
            ],
            options={
                'db_table': 'nhl_team',
            },
        ),
        migrations.CreateModel(
            name='Participates',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fantasy_league_name', models.ForeignKey(db_column='Fantasy_League_Name', on_delete=django.db.models.deletion.CASCADE, to='fantasy.FantasyLeague')),
                ('userid', models.ForeignKey(db_column='User_ID', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'db_table': 'participates',
            },
        ),
        migrations.CreateModel(
            name='SkaterTeams',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('fantasy_league_name', models.ForeignKey(db_column='Fantasy_League_Name', on_delete=django.db.models.deletion.CASCADE, related_name='SkaterTeams_Fantasy_League_Name', to='fantasy.FantasyLeague')),
            ],
            options={
                'db_table': 'skater_teams',
            },
        ),
        migrations.CreateModel(
            name='NhlGoalies',
            fields=[
                ('id', models.ForeignKey(db_column='id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='NHLGoalies_ID', serialize=False, to='fantasy.NhlPlayers')),
                ('wins', models.IntegerField(db_column='Wins', default=0)),
                ('losses', models.IntegerField(db_column='Losses', default=0)),
                ('overtime_losses', models.IntegerField(db_column='Overtime_Losses', default=0)),
                ('shots_against', models.IntegerField(db_column='Shots_Against', default=0)),
                ('saves', models.IntegerField(db_column='Saves', default=0)),
                ('shutouts', models.IntegerField(db_column='Shutouts', default=0)),
            ],
            options={
                'db_table': 'nhl_goalies',
            },
        ),
        migrations.CreateModel(
            name='NhlSkaters',
            fields=[
                ('id', models.ForeignKey(db_column='id', on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='NHLSkaters_ID', serialize=False, to='fantasy.NhlPlayers')),
                ('goals', models.IntegerField(db_column='Goals', default=0)),
                ('assists', models.IntegerField(db_column='Assists', default=0)),
                ('powerplay_goals', models.IntegerField(db_column='Powerplay_Goals', default=0)),
                ('powerplay_points', models.IntegerField(db_column='Powerplay_Points', default=0)),
                ('shorthanded_goals', models.IntegerField(db_column='Shorthanded_Goals', default=0)),
                ('shorthanded_points', models.IntegerField(db_column='Shorthanded_Points', default=0)),
                ('plus_minus', models.IntegerField(db_column='Plus_Minus', default=0)),
                ('penalty_minutes', models.IntegerField(db_column='Penalty_Minutes', default=0)),
                ('game_winning_goals', models.IntegerField(db_column='Game_Winning_Goals', default=0)),
                ('shots_on_goal', models.IntegerField(db_column='Shots_on_Goal', default=0)),
                ('center_flag', models.IntegerField(db_column='Center_Flag')),
                ('left_wing_flag', models.IntegerField(db_column='Left_Wing_Flag')),
                ('right_wing_flag', models.IntegerField(db_column='Right_Wing_Flag')),
                ('defencemen_flag', models.IntegerField(db_column='Defencemen_Flag')),
            ],
            options={
                'db_table': 'nhl_skaters',
            },
        ),
        migrations.AddField(
            model_name='skaterteams',
            name='playerid',
            field=models.ForeignKey(db_column='Player_ID', on_delete=django.db.models.deletion.CASCADE, related_name='SkaterTeams_ID', to='fantasy.NhlPlayers'),
        ),
        migrations.AddField(
            model_name='skaterteams',
            name='team_id',
            field=models.ForeignKey(db_column='Team_ID', on_delete=django.db.models.deletion.CASCADE, related_name='SkaterTeams_Team_ID', to='fantasy.FantasyTeam'),
        ),
        migrations.AddField(
            model_name='nhlplayers',
            name='team_name',
            field=models.ForeignKey(db_column='Team_Name', on_delete=django.db.models.deletion.CASCADE, to='fantasy.NhlTeam'),
        ),
        migrations.AddField(
            model_name='goalieteams',
            name='playerid',
            field=models.ForeignKey(db_column='Player_ID', on_delete=django.db.models.deletion.CASCADE, related_name='GoalieTeams_ID', to='fantasy.NhlPlayers'),
        ),
        migrations.AddField(
            model_name='goalieteams',
            name='team_id',
            field=models.ForeignKey(db_column='Team_ID', on_delete=django.db.models.deletion.CASCADE, related_name='GoaliesTeams_Team_ID', to='fantasy.FantasyTeam'),
        ),
        migrations.AddField(
            model_name='fantasyteam',
            name='userid',
            field=models.ForeignKey(db_column='Username', on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='fantasyleague',
            name='commissionerid',
            field=models.ForeignKey(db_column='Commissioner_ID', on_delete=django.db.models.deletion.CASCADE, to='fantasy.LeagueCommissioner'),
        ),
        migrations.AlterUniqueTogether(
            name='participates',
            unique_together={('userid', 'fantasy_league_name')},
        ),
        migrations.AlterUniqueTogether(
            name='nhlplayers',
            unique_together={('jersey_number', 'team_name')},
        ),
        migrations.AlterUniqueTogether(
            name='fantasyteam',
            unique_together={('fantasy_team_name', 'fantasy_league_name')},
        ),
    ]
