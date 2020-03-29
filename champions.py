import json

with open ('jsons\\champion.json', encoding="utf8") as JSON:
    champions_json = json.load(JSON)

champions = {}
for champion in champions_json['data']:
    
    champions.update({int (champions_json['data'][champion]['key']): champions_json['data'][champion]['id']})

def GetChampionName(id):
    return champions.get(id)
