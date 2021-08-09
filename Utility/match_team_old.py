# ==============================================================================
# File: match_team.py
# Project: Utility
# File Created: Tuesday, 15th June 2021 8:16:15 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 15th June 2021 8:16:17 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Finds the closest team match to a string
# useful when different data sources have things like "LA Chargers" and "Los Angeles Chargers"
# ==============================================================================


import sys
from os.path import abspath, dirname
import json

from fuzzywuzzy import fuzz
import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Match_Team:
    def __init__(self):
        pass

    @property
    def config(self):  # Property
        with open(ROOT_PATH + ".json", 'r') as f:
            config = json.load(f)
        return config

    def load_team_df(self, league):  # Top Level
        team_df = pd.read_csv(ROOT_PATH + f"/Data/Teams/{league}/{league}_Teams.csv")
        other_df = pd.read_csv(ROOT_PATH + f"/Data/Teams/{league}/{league}_Other_Teams.csv")
        full_df = pd.concat([team_df, other_df])
        return full_df

    def _corrections_dict(self, league):  # Specific Helper
        """
        loads the dict of corrections to be made when fuzzy-matching teams
        sometimes fuzzy-matching makes mistakes (e.g. TCU matches VCU Rams)
        """
        with open(ROOT_PATH + f"/Data/Teams/{league}/{league}_Corrections.json", 'r') as f:
            corrections_dict = json.load(f)
        return corrections_dict

    def fuzzy_match(self, league, teams, team_input):  # Top Level
        """
        finds the closest fuzzy-match in teams to the team_input
        - used to edit "LA Chargers" to "Los Angeles Chargers" etc
        """
        corrections_dict = self._corrections_dict(league)
        if team_input in corrections_dict:
            return corrections_dict[team_input], 100

        best_match = teams[0]
        best_match_ratio = fuzz.ratio(teams[0], team_input)
        for team in teams[1:]:
            current_ratio = fuzz.ratio(team, team_input)
            if current_ratio > best_match_ratio:
                best_match = team
                best_match_ratio = current_ratio
        return best_match, best_match_ratio

    def run(self, league, team_input):  # Run
        """
        finds the closest true team name match to team_input in a given league
        """
        team_df = self.load_team_df(league)
        teams = list(team_df['Team'])
        match, match_ratio = self.fuzzy_match(league, teams, team_input)
        return match, match_ratio


if __name__ == '__main__':
    x = Match_Team()
    self = x
    league = "NBA"
    # x.run()
