# ==============================================================================
# File: match_team.py
# Project: allison
# File Created: Sunday, 20th November 2022 11:45:04 am
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 20th November 2022 11:45:04 am
# Modified By: Dillon Koch
# -----
#
# -----
# class for matching an input string with an official team name from a given league
# ==============================================================================


import json
import sys
from os.path import abspath, dirname

import numpy as np

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Match_Team:
    def __init__(self, league):
        self.league = league
        self.teams_dict = self.load_teams_dict()
        self.valid_teams = self.list_valid_teams()

    def load_teams_dict(self):  # Top Level  __init__
        """
        loading dict with team names from /Data/Teams
        """
        path = ROOT_PATH + f"/Data/Teams/{self.league}.json"
        with open(path, 'r') as f:
            d = json.load(f)
        return d

    def list_valid_teams(self):  # Top Level  __init__
        """
        listing out all the valid teams (true and alt) for other programs
        """
        true = list(self.teams_dict["Teams"].keys())
        alt = []
        for team in true:
            alt += self.teams_dict['Teams'][team]['Names']

        other = self.teams_dict["Other"]
        return set(true + alt + other)

    def run(self, input_team):  # Run
        """
        attempting to return the "True" name of a given input_team str, if it's documented
        """
        true_teams = self.teams_dict['Teams'].keys()

        # * if it's already the true name, return
        if input_team in true_teams:
            return input_team

        # * if the input_team is an alternate name, return the correct true name
        for true_team in true_teams:
            alt_names = self.teams_dict['Teams'][true_team]['Names']
            if input_team in alt_names:
                return true_team

        # * if the team name is not a true team (like UNI or somthing) return "Other"
        if input_team in self.teams_dict["Other"]:
            return "Other"

        print(f"Input team name {input_team} not found in league {self.league}!")
        return np.nan


if __name__ == '__main__':
    x = Match_Team()
    self = x
    x.run()
