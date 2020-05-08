import requests
import json
import time
from apimanager import APIManager
import database as db
import configparser
import logging

SEASON10 = 1578657600000 # Timestamp in miliseconds - GMT: Friday, 10 January 2020 12:00:00 - season 10 start

def get_match_data(match, match_details, match_timeline, summoner_id):
    data = (None,)
    data += (int(match['gameId']),)
    data += (int(summoner_id),)
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
    # Read the config file
    config = configparser.ConfigParser()
    config.read('config.ini')
    # Setup progress logger
    progress_log = setup_logger('progress', str(config['PARMS']['s_logfile']) + '.log')
    # Init database connection and API manager
    database_connection = db.create_connection((config['DATABASE']['name'] + '.db'))
    API = APIManager(config['API']['key'])



    summoner_info = API.get_summoner_info(name=config['PARMS']['summoner'])
    time.sleep(1.4)
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

        # Clamp max_timestamp
        if max_timestamp < SEASON10:
            max_timestamp = SEASON10

        total_matches = 0

        # Main loop starts here 
        while not end:
            progress_log.info("Getting matches between {} and {}.".format(b_index, e_index))
            matches = API.get_match_history(summoner_info['accountId'], queue='420', beginIndex=str(b_index), endIndex=str(e_index), season='13')['matches']
            time.sleep(1.4)

            if matches is None:
                progress_log.error("Getting matches between {} and {} failed!".format(b_index, e_index))
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
                            match_data = get_match_data(match, match_details, match_timeline, summoner[0][0])
                            if match_data is None:
                                progress_log.error("Match data empty!")
                                end = True
                                break

                            participants = get_participants_data(match_details)
                            db.add_match(database_connection, match_data)
                            total_matches += 1

                            progress_log.info("Adding participants for match {}...".format(match['gameId']))

                            for participant_data in participants:
                                participant = API.get_summoner_info(summonerId=participant_data[8])
                                time.sleep(1.3)
                                
                                if participant is None:
                                    progress_log.warning("Summoner info empty!")
                                    participant_data += (999,)
                                else:
                                    participant_data += (int(participant['summonerLevel']),)

                                ranked_info = API.get_summoner_ranked_info(participant_data[8])
                                time.sleep(1.35)

                                participant_data += (int(round(time.time() * 1000)),)

                                if ranked_info is None:
                                    progress_log.warning("Ranked info not available!")
                                    participant_data += ("Unavailable",)
                                    participant_data += (-1,)
                                    participant_data += (-1,)

                                elif len(ranked_info) == 0:
                                    participant_data += ("Unranked",)
                                    participant_data += (-1,)
                                    participant_data += (-1,)

                                else:
                                    flag = False
                                    for ranked in ranked_info:
                                        if ranked['queueType'] == "RANKED_SOLO_5x5":
                                            participant_data += (str(ranked['tier']) + " " + str(ranked['rank']),)
                                            participant_data += (int(ranked['wins']),)
                                            participant_data += (int(ranked['losses']),)
                                            flag = True
                                    if not flag:
                                        progress_log.info("Soloqueue rank for summoner {} not found, treating as unranked...".format(participant_data[8]))
                                        participant_data += ("Unranked",)
                                        participant_data += (-1,)
                                        participant_data += (-1,)


                                if db.get_summoner(database_connection, participant_data[8]) == (-1):
                                    db.add_summoner(database_connection, get_summoner_data(participant))
                                db.add_participant(database_connection, participant_data)

            progress_log.info("Cycle {} finished, END = {}".format(i, end))

            progress_log.info("Total matches loaded: {}".format(total_matches))
            b_index += 100
            e_index += 100
            i += 1

    db.close_connection(database_connection)

    





def fix_timelines():
    config = configparser.ConfigParser()
    config.read('config.ini')
    progress_log = setup_logger('progress', str(config['PARMS']['s_logfile']) + '.log')
    API = APIManager(config['API']['key'])

    database_connection = db.create_connection((config['DATABASE']['name'] + '.db'))

    progress_log.info("Trying to fix missing timelines!")

    matches = db.get_missing_timelines(database_connection)

    if matches == (-1):
        progress_log.info("No missing timelines found!")
        return

    for match in matches:
        progress_log.info("Working on match {}...".format(match[0]))
        match_timeline = API.get_match_timeline(match[0])
        time.sleep(1.4)

        if match_timeline is None:
            progress_log.warning("Getting match timeline for matchId {} failed!".format(match[0]))
            continue

        db.update_timeline(database_connection, match[0], match_timeline)

def fix_ranks():
    config = configparser.ConfigParser()
    config.read('config.ini')
    progress_log = setup_logger('progress', str(config['PARMS']['s_logfile']) + '.log')
    API = APIManager(config['API']['key'])
    database_connection = db.create_connection((config['DATABASE']['name'] + '.db'))
    progress_log.info("Trying to fix missing ranked info!")

    summoners = db.get_missing_ranks(database_connection)

    if summoners == (-1):
        progress_log.info("No missing rankings found!")
        return
    
    for summoner in summoners:
        progress_log.info("Working on summoner {}, match {}...".format(summoner[0], summoner[1]))
        ranked_info = API.get_summoner_ranked_info(summoner[0])
        time.sleep(1.3)

        if ranked_info is None:
            progress_log.warning("Getting summoner ranked info for summoner {} failed!".format(summoner[0]))
            continue

        if len(ranked_info) == 0:
            progress_log.warning("Ranked info for summoner {} empty! Treating as unraked!".format(summoner[0]))
            rank = str("Unranked")
            wins = -1
            losses = -1
            db.update_ranking(database_connection, summoner[0], summoner[1], rank, wins, losses)
            continue

        flag = False
        for ranked in ranked_info:
            if ranked['queueType'] == "RANKED_SOLO_5x5":
                rank = str(ranked['tier']) + " " + str(ranked['rank'])
                wins = int(ranked['wins'])
                losses = int(ranked['losses'])
                db.update_ranking(database_connection, summoner[0], summoner[1], rank, wins, losses)
                flag = True
        
        if not flag:
            progress_log.info("Soloqueue rank for summoner {} not found, treating as unranked...".format(summoner[0]))
            rank = str("Unranked")
            wins = -1
            losses = -1
            db.update_ranking(database_connection, summoner[0], summoner[1], rank, wins, losses)

 


    
if __name__ == '__main__':
    main()
    # fix_timelines()
    # fix_ranks()