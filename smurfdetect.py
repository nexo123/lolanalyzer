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
        sql = """SELECT (p.timestamp - m.gameCreation) as diff, p.summonerId, p.summonerLevel, p.ranking, p.wins, p.losses
                    FROM participants p
                    JOIN matches m ON p.matchId = m.gameId
                    WHERE p.summonerId NOT IN ("2bt1NSSLsLBiXmgr4-VcGq-hl6na5GU5z7P0y94WTVwk0Go", "Sx_lzxM6YsTpezdNHt5AxQ7Cb2yqYMA9P1PbknusSmX1izo")
                    ORDER BY diff ASC;"""
        c.execute(sql)
        return c.fetchall()
    except Error as e:
        print(e)
        return -1

def get_data_age_diff(conn):
    try:
        c = conn.cursor()
        sql = """SELECT max(t1.diff), min(t1.diff)
                FROM (
                SELECT (p.timestamp - m.gameCreation) as diff
                FROM participants p
                JOIN matches m ON p.matchId = m.gameId
                WHERE p.summonerId NOT IN ("2bt1NSSLsLBiXmgr4-VcGq-hl6na5GU5z7P0y94WTVwk0Go", "Sx_lzxM6YsTpezdNHt5AxQ7Cb2yqYMA9P1PbknusSmX1izo")
                GROUP BY p.matchId
                ) t1"""
        c.execute(sql)
        return c.fetchall()
    except Error as e:
        print(e)
        return -1

def get_match_count(conn):
    try:
        c = conn.cursor()
        sql = """SELECT count(*)
                FROM matches;"""
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

    lvl_treshold_high = 75
    lvl_treshold_low = 65
    smurfs_count = 0
    counter = 0
    smurfs = []

    max_diff = get_data_age_diff(database_connection)[0][0]
    min_diff = get_data_age_diff(database_connection)[0][1]

    num_steps = lvl_treshold_high - lvl_treshold_low
    step = (max_diff - min_diff)/num_steps
    lvl_treshold = lvl_treshold_low

    teammates = get_teammates(database_connection)
    
    if teammates != (-1):
        current_diff = teammates[0][0]
        next_diff = current_diff + step

        for teammate in teammates:
            while teammate[0] > next_diff:
                current_diff = next_diff
                next_diff = current_diff + step
                lvl_treshold += 1

            if teammate[2] <= lvl_treshold:
                smurfs_count += 1
                smurfs.append(teammate)

            counter += 1

    # Second pass looking at winrates

    true_smurfs = []

    for smurf in smurfs:
        if smurf[3] == "Unavailable" or smurf[3] == "Unranked":
            true_smurfs.append(smurf)
        else:
            games_played = smurf[4] + smurf[5]
            winrate = smurf[4]/games_played
            if winrate >= 0.555:
                true_smurfs.append(smurf)

    match_count = get_match_count(database_connection)

    print("Smurfs found: %d, Games: %d, Smurfs to games ratio: 1/%f" % (len(true_smurfs), match_count[0][0], match_count[0][0]/len(true_smurfs)))

    # print(true_smurfs)
    
    db.close_connection(database_connection)

if __name__ == '__main__':
    main()