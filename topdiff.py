import sqlite3
from sqlite3 import Error
from os import path
import configparser
import logging
import database as db
import json

sql_top = """SELECT *
            FROM (
                SELECT matchId, role, lane, teamId, championId, stats
                FROM participants
                WHERE role="SOLO" AND lane="TOP" AND teamId=100
                ) t1
            INNER JOIN (
                SELECT matchId, role, lane, teamId, championId, stats
                FROM participants
                WHERE role="SOLO" AND lane="TOP" AND teamId=200
                ) t2
            ON t1.matchId = t2.matchId;"""

sql_jungle = """SELECT *
                FROM (
                    SELECT matchId, role, lane, teamId, championId, stats
                    FROM participants
                    WHERE role="NONE" AND lane="JUNGLE" AND teamId=100
                    ) t1
                INNER JOIN (
                    SELECT matchId, role, lane, teamId, championId, stats
                    FROM participants
                    WHERE role="NONE" AND lane="JUNGLE" AND teamId=200
                    ) t2
                ON t1.matchId = t2.matchId;"""

sql_bot = """SELECT *
            FROM (
                SELECT matchId, role, lane, teamId, championId, stats
                FROM participants
                WHERE role="DUO_CARRY" AND lane="BOTTOM" AND teamId=100
                ) t1
            INNER JOIN (
                SELECT matchId, role, lane, teamId, championId, stats
                FROM participants
                WHERE role="DUO_CARRY" AND lane="BOTTOM" AND teamId=200
                ) t2
            ON t1.matchId = t2.matchId;"""

sql_support = """SELECT *
                FROM (
                    SELECT matchId, role, lane, teamId, championId, stats
                    FROM participants
                    WHERE role="DUO_SUPPORT" AND lane="BOTTOM" AND teamId=100
                    ) t1
                INNER JOIN (
                    SELECT matchId, role, lane, teamId, championId, stats
                    FROM participants
                    WHERE role="DUO_SUPPORT" AND lane="BOTTOM" AND teamId=200
                    ) t2
                ON t1.matchId = t2.matchId;"""

sql_mid = """SELECT *
                FROM (
                    SELECT matchId, role, lane, teamId, championId, stats
                    FROM participants
                    WHERE role="SOLO" AND lane="MIDDLE" AND teamId=100
                    ) t1
                INNER JOIN (
                    SELECT matchId, role, lane, teamId, championId, stats
                    FROM participants
                    WHERE role="SOLO" AND lane="MIDDLE" AND teamId=200
                    ) t2
                ON t1.matchId = t2.matchId;"""

def get_data(conn, sql):
    try:
        c = conn.cursor()
        c.execute(sql)
        return c.fetchall()
    except Error as e:
        print(e)
        return -1

def evaluate(role, timeframe):
    config = configparser.ConfigParser()
    config.read('config.ini')
    database_connection = db.create_connection((config['DATABASE']['name'] + '.db'))

    queries = {
        1: sql_top,
        2: sql_jungle,
        3: sql_mid,
        4: sql_bot,
        5: sql_support
    }

    data = get_data(database_connection, queries.get(role))

    counter = 0
    
    for match in data:
        timeline_data = db.get_match(database_connection, match[0], "timeline")
        timeline = eval(timeline_data)

        team100_stats_data = match[5]
        team200_stats_data = match[11]

        team100_stats = eval(team100_stats_data)
        team200_stats = eval(team200_stats_data)


        team100_gold = 0
        team200_gold = 0

        for key, value in timeline['frames'][timeframe]['participantFrames'].items():
            if value['participantId'] == team100_stats['participantId']:
                team100_gold = value['totalGold']
            elif value['participantId'] == team200_stats['participantId']:
                team200_gold = value['totalGold']
        
        if (team100_gold > team200_gold) and team100_stats['win']:
            counter += 1
        elif (team100_gold < team200_gold) and team200_stats['win']:
            counter += 1
    
    return (len(data), counter)

    
def main():
    role = -1
    timeframe = -1

    roles = {
        1: "TOP",
        2: "JUNGLE",
        3: "MID",
        4: "BOT",
        5: "SUPPORT"
    }

    while True: 
        user_input = input("1: top\n2: jungle\n3: mid\n4: bot\n5: support\n0: exit\nPlease select which role to check: ")
        try:
            role = int(user_input)
            if role == 0: break
            elif roles.get(role) is None:
                print("Invalid input!")
                continue
        except:
            print("Invalid input!")
            continue
        user_input = input("Please enter timeframe in minutes (1 - 15), 0 to cancel: ")
        try: 
            timeframe = int(user_input)
            if timeframe == 0: continue
            elif timeframe < 0 or timeframe > 15:
                print("Invalid input!")
                continue
        except:
            print("Invalid input!")
            continue
        result = evaluate(role, timeframe)

        print("Results for %s ahead in gold at minute %d...\nSample size: %d, Positive: %d, Ratio: %f %%" % (roles.get(role), timeframe, result[0], result[1], result[1]/result[0]*100,))
        input("Press any key to continue...")

    
if __name__ == '__main__':
    main()