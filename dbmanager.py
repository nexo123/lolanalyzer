import sqlite3
from sqlite3 import Error
from os import path

class DBManager():

    sql_summoners_table = """ CREATE TABLE IF NOT EXISTS summoners (
                            summoner_id INTEGER PRIMARY KEY,
                            name text NOT NULL,
                            accountId text NOT NULL,
                            puuid text NOT NULL,
                            summonerId text NOT NULL UNIQUE
                        ); """

    sql_matches_table = """CREATE TABLE IF NOT EXISTS matches (
                            matchId INTEGER PRIMARY KEY,
                            gameId integer NOT NULL,
                            owner integer NOT NULL,
                            season integer NOT NULL,
                            champion integer NOT NULL,
                            role text NOT NULL,
                            lane text NOT NULL,
                            timestamp integer NOT NULL,
                            timeline blob NOT NULL,
                            gameCreation integer NOT NULL,
                            game Duration integer NOT NULL,
                            queueId integer NOT NULL,
                            mapId integer NOT NULL,
                            gameVersion text NOT NULL,
                            gameMode text NOT NULL,
                            gameType text NOT NULL,
                            teams blob NOT NULL,
                            FOREIGN KEY (owner) REFERENCES summoners (summoner_id)
                        ); """

    sql_patricipants_table = """CREATE TABLE IF NOT EXISTS participants (
                                matchId integer NOT NULL,
                                teamId integer NOT NULL,
                                championId integer NOT NULL,
                                spell1Id integer NOT NULL,
                                spell2Id integer NOT NULL,
                                stats blob NOT NULL,
                                accountId text NOT NULL,
                                summonerName text NOT NULL,
                                summonerId text NOT NULL,
                                FOREIGN KEY (matchId) REFERENCES matches (matchId)
                            ); """

    def create_connection(self, db_file):
        """ create a database connection to the SQLite database
            specified by db_file
        :param db_file: database file
        :return: Connection object or None
        """
        conn = None
        if path.exists(db_file):
            try:
                conn = sqlite3.connect(db_file)
                return conn
            except Error as e:
                print(e)
        else:
            try:
                conn = sqlite3.connect(db_file)
                self.init_database(conn)
                return conn
            except Error as e:
                print(e)  
    
        return conn
    
    def close_connection(self, conn):
        try:
            conn.close()
        except Error as e:
            print(e)

    def init_database(self, conn):
        """ create a table from the create_table_sql statement
        :param conn: Connection object
        :param create_table_sql: a CREATE TABLE statement
        :return:
        """
        try:
            c = conn.cursor()
            c.execute(self.sql_summoners_table)
            c.execute(self.sql_matches_table)
            c.execute(self.sql_patricipants_table)
            conn.commit()
        except Error as e:
            print(e)
    
    def insert_into_table(self, conn, table, values):
        try:
            c = conn.cursor()
            sql = "INSERT INTO " + table + " VALUES (" + values +")"
            c.execute(sql)
            conn.commit()
        except Error as e:
            print(e)


