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
import numpy as np


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
    # database_connection = db.create_connection("season2020_lProfessor.db")

    team_info = get_game_info(database_connection)

    snowball = 0
    anti_snowball = 0
    length_limit = 1800
    game_lengths = []
    n_games = 0

    for team in team_info:
        team_str = str(team[0])
        team_dict = eval(team_str)
        team_100 = eval(str(team_dict[0]))
        team_200 = eval(str(team_dict[1]))
        game_length = team[1]
        game_lengths.append(team[1])
        
        if game_length <= length_limit:
            n_games += 1
            if team_100['win'] == 'Win' and team_100['firstTower'] == True:
                snowball += 1
            if team_200['win'] == 'Win' and team_200['firstTower'] == True:
                snowball += 1
            
            if team_100['win'] == 'Win' and team_100['firstTower'] == False:
                anti_snowball += 1
            if team_200['win'] == 'Win' and team_200['firstTower'] == False:
                anti_snowball += 1


    print("1st turret + win + <= %.2f minutes: %d, Games analyzed: %d, Ratio %.2f %%" % (round(length_limit/60, 2), snowball, n_games, round(snowball/n_games*100, 2)))
    print("not 1st turret + win + <= %.2f minutes: %d, Games analyzed: %d, Ratio %.2f %%" % (round(length_limit/60, 2), anti_snowball, n_games, round(anti_snowball/n_games*100, 2)))
        
    print("50th percentile of game length: %.2f, average: %.2f " % (round(np.percentile(game_lengths, 50), 2), round(np.average(game_lengths), 2)))

    db.close_connection(database_connection)

if __name__ == '__main__':
    main()

