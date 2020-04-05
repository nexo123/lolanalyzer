import requests
import json
import configparser

class APIManager(object):
    
    def __init__(self, api_key):
        # create base url dictionary for API calls
        with open ('jsons\\base_urls.json', encoding="utf8") as JSON:
            self.base_urls = json.load(JSON)
        self.api_key = api_key

    def get_summoner_info(self, **kwargs):
        """Tries to retrieve summoner details based on provided id"""
        if len(kwargs) == 0:
            return None
        elif 'summonerId' in kwargs:
            url = self.base_urls['summoner_by_summonerId'] + kwargs.get("summonerId")
        elif 'accountId' in kwargs:
            url = self.base_urls['summoner_by_accountId'] + kwargs.get("accountId")
        elif 'puuid' in kwargs:
            url = self.base_urls['summoner_by_PUUID'] + kwargs.get("puuid")
        elif 'name' in kwargs:
            url = self.base_urls['summoner_by_name'] + kwargs.get("name")
        else:
            return None

        headers = {'X-Riot-Token': self.api_key}
        r = requests.get(url, headers = headers)

        if not (r.status_code == 200):
            print('Getting summoner details by {} failed! Status code: {}.'.format(kwargs, r.status_code))
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