# Generated by Django 2.1.7 on 2019-03-26 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('fantasy', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nhlteam',
            name='goals_against',
            field=models.IntegerField(db_column='Goals_Against', default=0),
        ),
        migrations.AlterField(
            model_name='nhlteam',
            name='goals_for',
            field=models.IntegerField(db_column='Goals_For', default=0),
        ),
        migrations.AlterField(
            model_name='nhlteam',
            name='losses',
            field=models.IntegerField(db_column='Losses', default=0),
        ),
        migrations.AlterField(
            model_name='nhlteam',
            name='overtime_losses',
            field=models.IntegerField(db_column='Overtime_Losses', default=0),
        ),
        migrations.AlterField(
            model_name='nhlteam',
            name='wins',
            field=models.IntegerField(db_column='Wins', default=0),
        ),
    ]
