import sqlite3
from sqlite3 import Error
from os import path

sql_summoners_table = """ CREATE TABLE IF NOT EXISTS summoners (
                        summoner_id INTEGER PRIMARY KEY,
                        name text NOT NULL,
                        accountId text NOT NULL,
                        puuid text NOT NULL,
                        summonerId text NOT NULL UNIQUE,
                        revisionDate int NOT NULL,
                        summonerLevel int NOT NULL
                    ); """

sql_matches_table = """CREATE TABLE IF NOT EXISTS matches (
                        matchId INTEGER PRIMARY KEY,
                        gameId integer NOT NULL UNIQUE,
                        owner integer NOT NULL,
                        season integer NOT NULL,
                        champion integer NOT NULL,
                        role text NOT NULL,
                        lane text NOT NULL,
                        timestamp integer NOT NULL,
                        timeline text NOT NULL,
                        gameCreation integer NOT NULL,
                        gameDuration integer NOT NULL,
                        queueId integer NOT NULL,
                        mapId integer NOT NULL,
                        gameVersion text NOT NULL,
                        gameMode text NOT NULL,
                        gameType text NOT NULL,
                        teams text NOT NULL,
                        FOREIGN KEY (owner) REFERENCES summoners (summoner_id)
                    ); """

sql_patricipants_table = """CREATE TABLE IF NOT EXISTS participants (
                            matchId integer NOT NULL,
                            teamId integer NOT NULL,
                            championId integer NOT NULL,
                            spell1Id integer NOT NULL,
                            spell2Id integer NOT NULL,
                            stats blob NOT NULL,
                            role text NOT NULL,
                            lane text NOT NULL,
                            summonerId text NOT NULL,
                            summonerLevel int NOT NULL,
                            timestamp int NOT NULL,
                            FOREIGN KEY (matchId) REFERENCES matches (gameId),
                            FOREIGN KEY (summonerId) REFERENCES summoners (summonerId)
                        ); """

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    if path.exists(db_file):
        try:
            conn = sqlite3.connect(db_file)
            conn.execute("PRAGMA foreign_keys = 1")
            return conn
        except Error as e:
            print(e)
    else:
        try:
            conn = sqlite3.connect(db_file)
            conn.execute("PRAGMA foreign_keys = 1")
            init_database(conn)
            return conn
        except Error as e:
            print(e)  

    return conn

def close_connection(conn):
    try:
        conn.close()
    except Error as e:
        print(e)

def init_database(conn):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(sql_summoners_table)
        c.execute(sql_matches_table)
        c.execute(sql_patricipants_table)
        conn.commit()
    except Error as e:
        print(e)

def add_summoner(conn, summoner_data):
    try:
        c = conn.cursor()
        sql = """INSERT INTO summoners VALUES (?, ?, ?, ?, ?, ?, ?);"""
        c.execute(sql, summoner_data)
        conn.commit()
        return c.lastrowid
    except Error as e:
        print(e)
        return -1

def add_match(conn, match_data):
    try:
        c = conn.cursor()
        sql = """INSERT INTO matches VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        c.execute(sql, match_data)
        conn.commit()
        return c.lastrowid
    except Error as e:
        print(e)
        return -1

def add_participant(conn, participant_data):
    try:
        c = conn.cursor()
        sql = """INSERT INTO participants VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"""
        c.execute(sql, participant_data)
        conn.commit()
        return c.lastrowid
    except Error as e:
        print(e)
        return -1

def get_max_of(conn, what):
    try:
        c = conn.cursor()
        sql = """SELECT MAX({}) FROM {};""".format(what[0], what[1])
        c.execute(sql)
        rows = c.fetchall()
        if rows[0][0] is None:
            return -1
        else:
            return rows[0][0]
    except Error as e:
        print(e)
        return -1

def get_summoner(conn, summoner_id):
    try:
        c = conn.cursor()
        sql = """SELECT summoner_id FROM summoners WHERE summonerId = "{}";""".format(summoner_id)
        c.execute(sql)
        rows = c.fetchall()
        if len(rows) > 0:
            return rows[0][0]
        else:
            return -1
    except Error as e:
        print(e)
        return -1
