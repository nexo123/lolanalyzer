import sqlite3
from sqlite3 import Error
from os import path
import configparser
import logging
import database as db
import json

def get_data(conn):
    try:
        c = conn.cursor()
        sql = """SELECT matchId, championId, stats
                    FROM participants;"""
        c.execute(sql)
        return c.fetchall()
    except Error as e:
        print(e)
        return -1
    
def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    database_connection = db.create_connection((config['DATABASE']['name'] + '.db'))

    data = get_data(database_connection)
    matches = []
    
    last_game_id = 0
    counter = 0
    
    for data_part in data:
        stats = eval(data_part[2])
        if last_game_id != data_part[0]:
            match = {'gameId': data_part[0]}
            participant = {'championId': data_part[1], 'championDamage': stats['totalDamageDealtToChampions']}
            match[stats['participantId']] = participant
            counter = 0
        if last_game_id == data_part[0]:
            participant = {'championId': data_part[1], 'championDamage': stats['totalDamageDealtToChampions']}
            match[stats['participantId']] = participant
            counter += 1
            if counter == 9: matches.append(match)
        
        last_game_id = data_part[0]
        
    adc_list = (523, 22, 51, 119, 81, 202, 222, 145, 429, 96, 236, 21, 15, 18, 29, 110, 67, 498)
    
    max_damages = []
    
    for match in matches:
        i = 1
        max_damage = 0
        max_damage_id = 0
        while i <= 10:
            participant = match[i]
            if participant['championDamage'] > max_damage:
                max_damage = participant['championDamage']
                max_damage_id = participant['championId']
            
            i += 1
        max_damages.append({'gameId': match['gameId'], 'championId': max_damage_id})
        
    adc_max = []
    
    for max_damage in max_damages:
        if max_damage['championId'] in adc_list:
            adc_max.append(max_damage)
            
    #adcs = [k['championId'] for k in max_damages if k.get('championId')]
    #adc_occurence = 
    
    print(len(adc_max))
    
    print("ADC most damage in: %d games, Total games: %d, Ratio: %f %%" % (len(adc_max), len(max_damages), len(adc_max)/len(max_damages)*100))
    
if __name__ == '__main__':
    main()