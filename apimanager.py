import requests
import json
import configparser

class APIManager(object):
    
    def __init__(self, summoner_name):
        self.summoner_name = summoner_name
        # create base url dictionary for API calls
        with open ('jsons\\base_urls.json', encoding="utf8") as JSON:
            self.base_urls = json.load(JSON)
        config = configparser.ConfigParser()
        config.read('config.ini')
        self.api_key = config['API']['key']
    
    def get_summoner_info(self):
        """Tries to retrieve encrypted account ID based on summoner name"""
        url = self.base_urls['summoner'] + self.summoner_name
        headers = {'X-Riot-Token': self.api_key}

        r = requests.get(url, headers = headers)
        if not (r.status_code == 200):
            print('Getting account id by summoner name {} failed!'.format(self.summoner_name))
            return None
        else:
            return r.json()

    def get_match_history(self, accountId, *args, **kwargs):
        first = True
        options = '?'
        for key, value in kwargs.items():
            if first:
                options += str(key) + '=' + str(value)
                first = False
            else:
                options += '&' + str(key) + '=' + str(value)

        url = self.base_urls['matchhistory'] + accountId + options
        headers = {'X-Riot-Token': self.api_key}

        r = requests.get(url, headers = headers)
        if not (r.status_code == 200):
            print('Getting match history by account id {} failed! Status code: {}.'.format(accountId, r.status_code))
            return None
        else:
            return r.json()
    
    def get_match_details(self, matchId):
        url = self.base_urls['matchdetail'] + str(matchId)
        headers = {'X-Riot-Token': self.api_key}

        r = requests.get(url, headers = headers)
        if not (r.status_code == 200):
            print('Getting match details with matchId {} failed! Status code: {}.'.format(matchId, r.status_code))
            return None
        else:
            return r.json()

    def get_match_timeline(self, matchId):
        url = self.base_urls['matchtimeline'] + str(matchId)
        headers = {'X-Riot-Token': self.api_key}

        r = requests.get(url, headers = headers)
        if not (r.status_code == 200):
            print('Getting match timeline with matchId {} failed! Status code: {}.'.format(matchId, r.status_code))
            return None
        else:
            return r.json()