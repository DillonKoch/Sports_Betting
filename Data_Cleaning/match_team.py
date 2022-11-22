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

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Match_Team:
    def __init__(self):
        pass

    def load_teams_dict(self, league):  # Top Level
        """
        loading dict with team names from /Data/Teams
        """
        path = ROOT_PATH + f"/Data/Teams/{league}.json"
        with open(path, 'r') as f:
            d = json.load(f)
        return d

    def run(self, league, input_team):  # Run
        """
        attempting to return the "True" name of a given input_team str, if it's documented
        """
        teams_dict = self.load_teams_dict(league)
        true_teams = teams_dict['Teams'].keys()

        # * if it's already the true name, return
        if input_team in true_teams:
            return input_team

        # * if the input_team is an alternate name, return the correct true name
        for true_team in true_teams:
            alt_names = teams_dict['Teams'][true_team]
            if input_team in alt_names:
                return true_team

        # * if the team name is not a true team (like UNI or somthing) return "Other"
        if input_team in teams_dict["Other"]:
            return "Other"

        raise ValueError(f"Input team name {input_team} not found in league {league}!")


if __name__ == '__main__':
    x = Match_Team()
    self = x
    x.run()
