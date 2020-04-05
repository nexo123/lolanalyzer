import sqlite3
from sqlite3 import Error
from os import path
import configparser
import logging
import database as db
import time

def get_teammates(conn):
    try:
        c = conn.cursor()
        sql = """SELECT participants.summonerId
                FROM participants
                WHERE summonerId NOT IN ("2bt1NSSLsLBiXmgr4-VcGq-hl6na5GU5z7P0y94WTVwk0Go", "Sx_lzxM6YsTpezdNHt5AxQ7Cb2yqYMA9P1PbknusSmX1izo");"""
        c.execute(sql)
        return c.fetchall()
    except Error as e:
        print(e)
        return -1

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    database_connection = db.create_connection((config['DATABASE']['name'] + '.db'))

if __name__ == '__main__':
    main()