import requests
import json
import time
from champions import GetChampionName
from apimanager import APIManager
import database as db
import configparser
import logging

SEASON10 = 1578657600000 # Timestamp in miliseconds - GMT: Friday, 10 January 2020 12:00:00 - season 10 start

def get_match_data(match, match_details, match_timeline, summoner_id):
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
        participant_data += (str(match_details['participantIdentities'][participant_id - 1]['player']['summonerId']),)
        participant_list.append(participant_data)

    return participant_list

def get_summoner_data(summoner_info):
    data = (None,)
    data += (str(summoner_info['name']),)
    data += (str(summoner_info['accountId']),)
    data += (str(summoner_info['puuid']),)
    data += (str(summoner_info['id']),)
    data += (int(summoner_info['revisionDate']),)
    data += (int(summoner_info['summonerLevel']),)

    return data

def setup_logger(name, log_file, level=logging.INFO):
    formatter = logging.Formatter('(%(asctime)s) %(levelname)s: %(message)s', '%Y-%m-%d %H:%M:%S')

    handler = logging.FileHandler(log_file)        
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger

def main():
    progress_log = setup_logger('progress', 'log_progress.log')
    config = configparser.ConfigParser()
    config.read('config.ini')
    API = APIManager(config['API']['key'])
    summoner_info = API.get_summoner_info(name=config['PARMS']['summoner'])
    time.sleep(1.4)

    database_connection = db.create_connection((config['DATABASE']['name'] + '.db'))
    end = False

    if not summoner_info is None:
        b_index = int(config['PARMS']['bIndex'])
        e_index = int(config['PARMS']['eIndex'])
        i = 1

        summoner = db.get_summoner(database_connection, summoner_info['id'])

        if summoner == -1:
            summoner_data = get_summoner_data(summoner_info)
            summoner = db.add_summoner(database_connection, summoner_data)

        if bool(int(config['PARMS']['t_override'])):
            max_timestamp = 0
        else:
            max_timestamp = db.get_max_of(database_connection, ('timestamp', 'matches')) 

        # clamp max_timestamp
        if max_timestamp < SEASON10:
            max_timestamp = SEASON10

        while not end:
            progress_log.info("Gertting matches between {} and {}.".format(b_index, e_index))
            matches = API.get_match_history(summoner_info['accountId'], queue='420', beginIndex=str(b_index), endIndex=str(e_index), season='13')['matches']
            time.sleep(1.4)

            if matches is None:
                progress_log.warning("Getting matches between {} and {} failed!".format(b_index, e_index))
                break
            else:
                for match in matches:
                    progress_log.info("Working on match {}...".format(match['gameId']))

                    if int(match['timestamp']) < max_timestamp:
                        progress_log.info("Timestamp limit reached! Exiting.")
                        end = True
                        break

                    if db.get_match(database_connection, match['gameId']) != (-1):
                        progress_log.info("Skipping match {}, already exists".format(match['gameId']))
                    else:                        
                        match_details = API.get_match_details(match['gameId'])
                        time.sleep(1.4)
                        match_timeline = API.get_match_timeline(match['gameId'])
                        time.sleep(1.4)

                        if match_timeline is None:
                            progress_log.warning("Getting match timeline for matchId {} failed!".format(match['gameId']))
                            match_timeline = "Unavailable"

                        if match_details is None:
                            progress_log.warning("Getting match details for matchId {} failed!".format(match['gameId']))
                            continue
                        else:
                            match_data = get_match_data(match, match_details, match_timeline, summoner)
                            if match_data is None:
                                progress_log.warning("Match data empty!")
                                end = True
                                break
                            participants = get_participants_data(match_details)
                            db.add_match(database_connection, match_data)

                            progress_log.info("Adding participants for match {}...".format(match['gameId']))

                            for participant_data in participants:
                                participant = API.get_summoner_info(summonerId=participant_data[8])
                                time.sleep(1.4)
                                participant_data += (int(participant['summonerLevel']),)
                                participant_data += (int(round(time.time() * 1000)),)
                                if db.get_summoner(database_connection, participant_data[8]) == (-1):
                                    db.add_summoner(database_connection, get_summoner_data(participant))
                                db.add_participant(database_connection, participant_data)

            progress_log.info("Cycle {} finished, END = {}".format(i, end))
            b_index += 100
            e_index += 100
            i += 1

    db.close_connection(database_connection)

def test():
    return
    
if __name__ == '__main__':
    main()
    # test()