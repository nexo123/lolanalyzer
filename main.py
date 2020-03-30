import requests
import json
import time
from champions import GetChampionName
from apimanager import APIManager
import database as db
import configparser

def get_match_data(match, match_details, match_timeline, summoner_id, limiter):
    if int(match['timestamp']) < limiter:
        return None
    else:
        data = (None,)
        data += (int(match['gameId']),)
        data += (summoner_id,)
        data += (int(match['season']),)
        data += (int(match['champion']),)
        data += (str(match['role']),)
        data += (str(match['lane']),)
        data += (int(match['timestamp']),)
        data += (str(match_timeline),)
        data += (int(match_details['gameCreation']),)
        data += (int(match_details['gameDuration']),)
        data += (int(match_details['queueId']),)
        data += (int(match_details['mapId']),)
        data += (str(match_details['gameVersion']),)
        data += (str(match_details['gameMode']),)
        data += (str(match_details['gameType']),)
        data += (str(match_details['teams']),)
        return data

def get_participants_data(match_details):
    participant_list = []
    for participant in match_details['participants']:
        participant_data = (match_details['gameId'],)
        participant_id = int(participant['participantId'])
        participant_data += (int(participant['teamId']),)
        participant_data += (int(participant['championId']),)
        participant_data += (int(participant['spell1Id']),)
        participant_data += (int(participant['spell2Id']),)
        participant_data += (str(participant['stats']),)
        participant_data += (str(participant['timeline']['role']),)
        participant_data += (str(participant['timeline']['lane']),)
        participant_data += (str(match_details['participantIdentities'][participant_id - 1]['player']['accountId']),)
        participant_data += (str(match_details['participantIdentities'][participant_id - 1]['player']['summonerName']),)
        participant_data += (str(match_details['participantIdentities'][participant_id - 1]['player']['summonerId']),)
        participant_list.append(participant_data)

    return participant_list

def get_summoner_data(summoner_info):
    data = (None,)
    data += (str(summoner_info['name']),)
    data += (str(summoner_info['accountId']),)
    data += (str(summoner_info['puuid']),)
    data += (str(summoner_info['id']),)

    return data

def main():
    config = configparser.ConfigParser()
    config.read('config.ini')
    API = APIManager(config['Summoner']['name'])
    summoner_info = API.get_summoner_info()
    database_connection = db.create_connection((config['Database']['name'] + '.db'))
    end = False

    if not summoner_info is None:
        b_index = 0
        e_index = 100
        i = 1
        summoner_data = get_summoner_data(summoner_info)
        summoner = db.add_summoner(database_connection, summoner_data)
        time.sleep(1.5)

        while ((not end) and (summoner > 0)):
            matches = API.get_match_history(summoner_info['accountId'], queue='420', beginIndex=str(b_index), endIndex=str(e_index), season='13')['matches']
            time.sleep(1.5)

            if not matches is None:
                for match in matches:
                    match_details = API.get_match_details(match['gameId'])
                    time.sleep(1.5)
                    match_timeline = API.get_match_timeline(match['gameId'])
                    time.sleep(1.5)

                    if match_timeline is None:
                        match_timeline = "Unavailable"

                    if match_details is None:
                        continue
                    else:
                        match_data = get_match_data(match, match_details, match_timeline, summoner, 1578657600000)
                        if match_data is None:
                            end = True
                            break
                        participants = get_participants_data(match_details)
                        
                        db.add_match(database_connection, match_data)
                        for participant_data in participants:
                            db.add_participant(database_connection, participant_data)
            else:
                break
            print("Epoch {} finished, END = {}".format(i, end))
            b_index += 100
            e_index += 100
            i += 1

    db.close_connection(database_connection)

if __name__ == '__main__':
    main()