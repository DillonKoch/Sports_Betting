# ==============================================================================
# File: match_team.py
# Project: allison
# File Created: Sunday, 8th August 2021 9:33:10 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 8th August 2021 9:33:10 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Finds the closest matches from an input string to the official ESPN team names
# ==============================================================================


import json
import os
import sys
from operator import itemgetter
from os.path import abspath, dirname

import pandas as pd
from fuzzywuzzy import fuzz

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class Match_Team:
    def __init__(self):
        pass

    def load_team_dict(self, league):  # Top Level
        """
        loads the team JSON dict from /Data/Teams/
        """
        path = ROOT_PATH + f"/Data/Teams/{league}_Teams.json"
        with open(path) as f:
            team_dict = json.load(f)
        return team_dict

    def existing_team_names(self, team_dict):  # Top Level
        """
        loads all the team names (official and other) in the JSON file
        """
        names = list(team_dict['Teams'].keys())
        other_teams = team_dict['Other Teams']
        other_names = []
        for name in names:
            current_other_names = team_dict['Teams'][name]['Other Names']
            other_names.extend(current_other_names)
        all_names = names + other_names + other_teams
        return names, all_names

    def _load_odds_team_names(self, league):  # Specific Helper load_team_names_all_data
        """
        Loads team names for a league in all Odds data
        """
        folder = ROOT_PATH + f"/Data/Odds/{league}/"
        df_paths = listdir_fullpath(folder)
        df = pd.concat([pd.read_excel(path) for path in df_paths])
        teams = list(set(list(df['Team'])))
        return teams

    def load_team_names_all_data(self, league):  # Top Level
        """
        loads the team names from all data sources scraped
        """
        # TODO add more specific helpers when I add more data sources
        odds_names = self._load_odds_team_names(league)
        all_names = odds_names
        return all_names

    def find_matches(self, existing_names, team_name):  # Top Level
        """
        finds the top 10 matches for a team name not in ESPN names
        """
        existing_dist_combos = []
        for existing_name in existing_names:
            # lev_dist = distance(existing_name, team_name)
            lev_dist = fuzz.ratio(existing_name, team_name)
            existing_dist_combos.append((existing_name, lev_dist))

        existing_dist_combos = sorted(existing_dist_combos, key=itemgetter(1), reverse=True)
        for i, combo in enumerate(existing_dist_combos[:10]):
            team, dist = combo
            print(f"({i}) {dist} - {team}")
        return [item[0] for item in existing_dist_combos]

    def update_team_dict(self, team_dict, team_name, matches, real_team_index):  # Top Level
        if real_team_index == 'O':
            team_dict['Other Teams'] = team_dict['Other Teams'] + [team_name]
        elif real_team_index != '':
            real_team = matches[int(real_team_index)]
            team_dict['Teams'][real_team]['Other Names'] += [team_name]
        return team_dict

    def save_team_dict(self, league, team_dict):  # Top Level
        path = ROOT_PATH + f"/Data/Teams/{league}_Teams.json"
        with open(path, 'w') as f:
            json.dump(team_dict, f)

    def run(self, league):  # Run
        # load team names in all data sources for all leagues
        # in command line, show non-matched team, and top 10 matches
        # accept user input 1-10 to automatically add the name to the JSON
        team_dict = self.load_team_dict(league)
        official_names, existing_names = self.existing_team_names(team_dict)
        team_names_all_data = self.load_team_names_all_data(league)
        print(len(team_names_all_data))
        for i, team_name in enumerate(team_names_all_data):
            print(i)
            if team_name not in existing_names:
                print('-' * 50)
                print(team_name)
                matches = self.find_matches(official_names, team_name)
                real_team_index = input("replacement index: ")
                team_dict = self.update_team_dict(team_dict, team_name, matches, real_team_index)
                self.save_team_dict(league, team_dict)


if __name__ == '__main__':
    x = Match_Team()
    self = x
    for league in ["NFL", "NBA", "NCAAF", "NCAAB"]:
        print('-' * 50)
        print(league)
        print('-' * 50)
        x.run(league)
