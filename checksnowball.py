import sqlite3
from sqlite3 import Error
from os import path
import configparser
import logging
import database as db
import time
import json


def get_game_info(conn):
    try:
        c = conn.cursor()
        sql = """SELECT teams FROM matches;"""
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

    for team in team_info:
        team_str = str(team[0])
        team_dict = eval(team_str)
        team_100 = eval(str(team_dict[0]))
        team_200 = eval(str(team_dict[1]))

        counter += 1
        
        if team_100['win'] == 'Win' and team_100['firstTower'] == True:
            snowball += 1
        if team_200['win'] == 'Win' and team_100['firstTower'] == True:
            snowball += 1

    print("1st turret + win: %d, Games analyzed: %d, Ratio %f %%" % (snowball, counter, snowball/counter*100))
        

    db.close_connection(database_connection)

if __name__ == '__main__':
    main()

