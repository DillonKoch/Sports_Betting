from os.path import abspath, dirname
import sys

import os


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

import json


def config(path):  # Property
    with open(path, 'r') as f:
        config = json.load(f)
    return config


for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
    # with open(f"{league}_Teams.json") as f:
    #     old = json.load(f)

    with open(f"{league}.json") as f:
        cur = json.load(f)

    # teams = list(cur['Teams'].keys())
    # cur_2 = {"Teams": {team: {"Names": cur['Teams'][team], "Schedule": old['Teams'][team]['Schedule']} for team in teams},
    #          "Other": cur['Other']}
    for team in cur['Teams'].keys():
        cur['Teams'][team]['Roster'] = cur['Teams'][team]['Schedule'].replace('schedule', 'roster')

    with open(f"{league}.json", 'w') as f:
        json.dump(cur, f)
