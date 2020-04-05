import sqlite3
from sqlite3 import Error
from os import path
import configparser
import logging
from apimanager import APIManager
import database as db
import time

def get_unique_participants(conn):
    try:
        c = conn.cursor()
        sql = """SELECT DISTINCT summonerId FROM participants;"""
        c.execute(sql)
        return c.fetchall()
    except Error as e:
        print(e)
        return -1

def main():
    logging.basicConfig(filename='log.log', level=logging.DEBUG)
    config = configparser.ConfigParser()
    config.read('config.ini')
    API = APIManager(config['Summoner']['name'])
    database_connection = db.create_connection((config['Database']['name'] + '.db'))
    
    unique_participants = get_unique_participants(database_connection)

if __name__ == '__main__':
    main()