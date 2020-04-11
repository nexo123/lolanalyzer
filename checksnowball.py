import sqlite3
from sqlite3 import Error
from os import path
import configparser
import logging
import database as db
import time
import json
import matplotlib.pyplot as plt
import seaborn as sns


def get_game_info(conn):
    try:
        c = conn.cursor()
        sql = """SELECT teams, gameDuration FROM matches;"""
        c.execute(sql)
        return c.fetchall()
    except Error as e:
        print(e)
        return -1

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    database_connection = db.create_connection((config['DATABASE']['name'] + '.db'))

    team_info = get_game_info(database_connection)

    counter = 0
    snowball = 0
    anti_snowball = 0
    game_lengts = []

    for team in team_info:
        team_str = str(team[0])
        team_dict = eval(team_str)
        team_100 = eval(str(team_dict[0]))
        team_200 = eval(str(team_dict[1]))
        game_length = team[1]
        game_lengts.append(team[1])


        counter += 1
        
        if team_100['win'] == 'Win' and team_100['firstTower'] == True and game_length <= 1500:
            snowball += 1
        if team_200['win'] == 'Win' and team_200['firstTower'] == True and game_length <= 1500:
            snowball += 1
        
        if team_100['win'] == 'Win' and team_100['firstTower'] == False and game_length <= 1500:
            anti_snowball += 1
        if team_200['win'] == 'Win' and team_200['firstTower'] == False and game_length <= 1500:
            anti_snowball += 1


    print("1st turret + win + <= 25 minutes: %d, Games analyzed: %d, Ratio %f %%" % (snowball, counter, snowball/counter*100))
    print("not 1st turret + win + <= 25 minutes: %d, Games analyzed: %d, Ratio %f %%" % (anti_snowball, counter, anti_snowball/counter*100))

    # matplotlib histogram
    
    plt.hist(game_lengts, color = 'blue', edgecolor = 'black',
         bins = int(3400/25))

    # # seaborn histogram
    # sns.distplot(flights['arr_delay'], hist=True, kde=False, 
    #             bins=int(180/5), color = 'blue',
    #             hist_kws={'edgecolor':'black'})
    # Add labels
    plt.title('Histogram of Game Lengths')
    plt.xlabel('Game Length (sec)')
    plt.ylabel('Games')
        

    db.close_connection(database_connection)

if __name__ == '__main__':
    main()

