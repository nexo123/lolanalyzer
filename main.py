import requests
import json
from champions import GetChampionName

apikey = 'RGAPI-85a3a340-e04a-4596-a066-574996513cf2'
summoner_name = 'Worst Lux Galaxy'

# create base url dictionary for API calls
with open ('jsons\\base_urls.json', encoding="utf8") as JSON:
    base_urls = json.load(JSON)

# get account ID based on summoner name

def GetAccountID():
    """Tries to retrieve encrypted account ID based on summoner name"""
    url = base_urls['summoner'] + summoner_name
    headers = {'X-Riot-Token': apikey}

    r = requests.get(url, headers = headers)
    if not (r.status_code == 200):
        print('Getting account id by summoner name {} failed!'.format(summoner_name))
        return None
    else:
        response_json = r.json()
        return response_json['accountId']

def GetMatchHistory(accountId):
    url = base_urls['matchhistory'] + accountId + '?queue=420'
    headers = {'X-Riot-Token': apikey}

    r = requests.get(url, headers = headers)
    if not (r.status_code == 200):
        print('Getting account id by summoner name {} failed!'.format(summoner_name))
        return None
    else:
        return r.json()

champ = GetMatchHistory(GetAccountID())['matches'][0]['champion']
print(GetChampionName(champ))