# Generated by Django 2.1.7 on 2019-03-26 05:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0003_auto_20190325_2345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fantasyleague',
            name='assists_weight',
            field=models.DecimalField(db_column='Assists_Weight', decimal_places=1, default=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='game_winning_goals_weight',
            field=models.DecimalField(db_column='Game_Winning_Goals_Weight', decimal_places=1, default=1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='goals_against_average_weight',
            field=models.DecimalField(db_column='Goals_Against_Average_Weight', decimal_places=1, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='goals_against_weight',
            field=models.DecimalField(db_column='Goals_Against_Weight', decimal_places=1, default=-1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='goals_weight',
            field=models.DecimalField(db_column='Goals_Weight', decimal_places=1, default=3, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='losses_weight',
            field=models.DecimalField(db_column='Losses_Weight', decimal_places=1, default=-2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='overtime_losses_weight',
            field=models.DecimalField(db_column='Overtime_Losses_Weight', decimal_places=1, default=-2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='penalty_minutes_weight',
            field=models.DecimalField(db_column='Penalty_Minutes_Weight', decimal_places=1, default=0.5, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='plus_minus',
            field=models.DecimalField(db_column='+/-_Weight', decimal_places=1, default=1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='powerplay_goals_weight',
            field=models.DecimalField(db_column='Powerplay_Goals_Weight', decimal_places=1, default=1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='saves_percentage_weight',
            field=models.DecimalField(db_column='Saves_Percentage_Weight', decimal_places=1, default=0, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='saves_weight',
            field=models.DecimalField(db_column='Saves_Weight', decimal_places=1, default=0.2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='shorthanded_assists_weight',
            field=models.DecimalField(db_column='Shorthanded_Assists_Weight', decimal_places=1, default=1, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='shorthanded_goals_weight',
            field=models.DecimalField(db_column='Shorthanded_Goals_Weight', decimal_places=1, default=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='shots_on_goal_weight',
            field=models.DecimalField(db_column='Shots_on_Goal_Weight', decimal_places=1, default=0.4, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='shutouts_weight',
            field=models.DecimalField(db_column='Shutouts_Weight', decimal_places=1, default=2, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyleague',
            name='wins_weight',
            field=models.DecimalField(db_column='Wins_Weight', decimal_places=1, default=4, max_digits=10),
        ),
        migrations.AlterField(
            model_name='fantasyteam',
            name='fantasy_points',
            field=models.IntegerField(db_column='Fantasy_Points', default=0),
        ),
    ]
