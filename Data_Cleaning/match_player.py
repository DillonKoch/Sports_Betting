# ==============================================================================
# File: match_player.py
# Project: allison
# File Created: Tuesday, 16th November 2021 1:39:45 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 16th November 2021 1:39:46 pm
# Modified By: Dillon Koch
# -----
#
# -----
# matching players' dash names from ESPN and Covers so we can merge player stats and injuries
# ==============================================================================

import copy
import json
import os
import sys
from os.path import abspath, dirname

import Levenshtein as lev
import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Match_Player:
    def __init__(self, league):
        self.league = league
        self.json_path = ROOT_PATH + f"/Data/Covers/{self.league}/Player_Matches.json"
        self.espn_players_df = pd.read_csv(ROOT_PATH + f"/Data/ESPN/{self.league}/Players.csv")
        self.injuries_df = pd.read_csv(ROOT_PATH + f"/Data/Covers/{self.league}/Injuries.csv")

    def load_player_json(self):  # Top Level
        """
        loading the player_json file if it exists, or starting a new one
        """
        if os.path.exists(self.json_path):
            with open(self.json_path, 'r') as f:
                player_json = json.load(f)
        else:
            player_json = {"No Matches": []}
        return player_json

    def load_espn_players(self):  # Top Level
        """
        makes a list of all the ESPN players' dash names
        """
        player_names = list(self.espn_players_df['Player'])
        player_names = list(set(player_names))
        player_dash_names = [player_name.strip().lower().replace(' ', '-') for player_name in player_names]
        return player_dash_names

    def load_covers_players(self):  # Top Level
        """
        makes a list of all the Covers players' dash names
        """
        covers_dash_names = list(self.injuries_df['Player'])
        return list(set(covers_dash_names))

    def find_closest_matches(self, covers_player, espn_players):  # Top Level
        """
        """
        espn_players_copy = copy.deepcopy(espn_players)
        espn_players_sorted = sorted(espn_players_copy, key=lambda x: lev.distance(x, covers_player))
        return espn_players_sorted[:10]

    def find_user_match(self, covers_player, closest_matches):  # Top Level
        """
        """
        print('-' * 50)
        print('\n\n\n')
        print(covers_player)
        for i, closest_match in enumerate(closest_matches):
            print(f"{i}: {closest_match}")

        user_match = input("Match num: ")
        if user_match == '':
            return None
        correction = closest_matches[int(user_match)]
        return correction

    def update_player_json(self, covers_player, user_match, player_json):  # Top Level
        """
        """
        if user_match is None:
            player_json['No Matches'].append(covers_player)
        else:
            player_json[covers_player] = user_match

        with open(self.json_path, 'w') as f:
            json.dump(player_json, f)
        return player_json

    def run(self):  # Run
        player_json = self.load_player_json()
        espn_players = self.load_espn_players()
        covers_players = self.load_covers_players()
        for i, covers_player in enumerate(covers_players):
            print(f"{i}/{len(covers_players)}")
            if (covers_player not in espn_players) and (covers_player not in player_json):
                closest_matches = self.find_closest_matches(covers_player, espn_players)
                user_match = self.find_user_match(covers_player, closest_matches)
                player_json = self.update_player_json(covers_player, user_match, player_json)
        print("DONE")


if __name__ == '__main__':
    # for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
    for league in ['NBA']:
        x = Match_Player(league)
        self = x
        x.run()
