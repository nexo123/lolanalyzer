import json

with open ('jsons\\champion.json', encoding="utf8") as JSON:
    champions_json = json.load(JSON)

with open ('jsons\\summoner_spells.json', encoding="utf8") as JSON:
    summoner_spells_json = json.load(JSON)

champions = {}
for champion in champions_json['data']:
    champions.update({int (champions_json['data'][champion]['key']): champions_json['data'][champion]['name']})

summoner_spells = {}
for summoner_spell in summoner_spells_json['data']:
    summoner_spells.update({int (summoner_spells_json['data'][summoner_spell]['key']): summoner_spells_json['data'][summoner_spell]['name']})


def GetChampionName(id):
    return champions.get(id)

def GetSummonerSpellName(id):
    return summoner_spells.get(id)

def main():
    select = input("1. champion\n2. summoner spell\n0. exit\nPlease enter what you want to decode: ")
    while select != "0":
        if select == "1":
            champion = input("Please enter champion ID: ")
            while champion != "exit":
                print("Your champion is: %s" % GetChampionName(int(champion)))
                champion = input("Please enter champion ID: ")
        elif select == "2":
            spell = input("Please enter spell ID: ")
            while spell != "exit":
                print("Your champion is: %s" % GetSummonerSpellName(int(spell)))
                spell = input("Please enter spell ID: ")
        else:
            print("Unknown option!")
        select = input("1. champion\n2. summoner spell\n0. exit\nPlease enter what you want to decode: ")
            


if __name__ == '__main__':
    main()