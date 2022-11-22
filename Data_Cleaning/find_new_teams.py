# ==============================================================================
# File: find_new_teams.py
# Project: allison
# File Created: Sunday, 20th November 2022 2:56:15 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 20th November 2022 2:56:15 pm
# Modified By: Dillon Koch
# -----
#
# -----
# * Trying to find new team names in all data sources
# * if new team is found, adding to /Data/Teams/ json file
# * may not be a whole new team necessarily, but a new name for them (Commanders)
# ==============================================================================

import json
import os
import sys
from operator import itemgetter
from os.path import abspath, dirname

import pandas as pd
from fuzzywuzzy import fuzz
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class Find_New_Teams:
    def __init__(self, league):
        self.league = league

        # * loading team JSON file from /Data/Teams
        self.json_path = ROOT_PATH + f"/Data/Teams/{league}.json"
        with open(self.json_path, 'r') as f:
            self.teams = json.load(f)

    def load_existing(self):  # Top Level
        """
        loading true, alternate, "other" names that are already saved in the /Data/Teams json
        """
        true = list(self.teams['Teams'].keys())
        alt = [subitem for item in self.teams['Teams'].values() for subitem in item]
        other = self.teams['Other']
        return true + alt + other

    def load_sbro(self):  # Top Level
        """
        loading all team names in Sportsbook Reviews Online data
        """
        folder = ROOT_PATH + f"/Data/Odds/{self.league}"
        paths = listdir_fullpath(folder)

        sbro_teams = []
        for path in tqdm(paths):
            df = pd.read_excel(path)
            teams = list(df['Team'])
            teams = [team for team in teams if isinstance(team, str)]  # * sometimes empty rows show up
            sbro_teams = list(set(sbro_teams + teams))

        return sbro_teams

    def load_esb(self):  # Top Level
        """
        loading all team names in Elite Sportsbook data
        """
        # TODO
        return []

    def load_espn(self):  # Top Level
        """
        loading all team names in ESPN data
        """
        # TODO
        return []

    def closest_matches(self, team):  # Top Level
        """
        given a team string, this finds the 10 closest matches among true team names
        """
        distances = []
        for true_team in list(self.teams['Teams'].keys()):
            dist = fuzz.ratio(team, true_team)
            distances.append((true_team, dist))

        distances = sorted(distances, key=itemgetter(1))
        return distances[-10:][::-1]

    def update_team(self, team, correction, distances):  # Top Level
        """
        given a team string that had no match and a correction, this updates the Teams JSON file in /Data/Teams
        """
        if correction == 'O':
            self.teams['Other'].append(team)

        elif correction in '0123456789':
            idx = int(correction)
            true_team = distances[idx][0]
            self.teams['Teams'][true_team].append(team)

        with open(self.json_path, 'w') as f:
            json.dump(self.teams, f)

    def run(self):  # Run
        existing_teams = self.load_existing()
        sbro_teams = self.load_sbro()
        esb_teams = self.load_esb()
        espn_teams = self.load_espn()

        all_teams = sbro_teams + esb_teams + espn_teams
        for team in all_teams:
            if team not in existing_teams:
                print("-" * 50)
                print(f"COULD NOT FIND {team}")
                distances = self.closest_matches(team)
                for i, distance in enumerate(distances):
                    print(f"{i}: {distance[0]} - {distance[1]}")
                correction = input("Input correct team 1-10 or 'O' for other: ")
                self.update_team(team, correction, distances)


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        print(league)
        x = Find_New_Teams(league)
        self = x
        x.run()
