import requests
import json
import time
from champions import GetChampionName
from apimanager import APIManager
import database as db


def main():
    API = APIManager('Worst Lux Galaxy')
    summoner_info = API.get_summoner_info()

    matches = API.get_match_history(summoner_info['accountId'])['matches']
    details = API.get_match_details(matches[0]['gameId'])
    
    database = db.create_connection('season2020.db')
    values = "NULL, \'" + summoner_info['name'] + "\', \'" + summoner_info['accountId'] + "\', \'" + summoner_info['puuid'] + "\', \'" + summoner_info['id'] + "\'"
    db.insert_into_table(database, 'summoners', values)
    print(details)
    # accountId = API.GetAccountID()
    # time.sleep(0.5)
    # match_history = API.GetMatchHistory(accountId)
    # time.sleep(0.5)
    # print(API.GetMatchDetail(match_history['matches'][0]['gameId']))

    # champ = GetMatchHistory(GetAccountID())['matches'][1]['champion']
    # champ = API.GetMatchHistory(API.GetAccountID())['matches'][1]['champion']
    # print(GetChampionName(champ))

if __name__ == '__main__':
    main()