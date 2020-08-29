# ==============================================================================
# File: odds_team_conversions_test.py
# Project: Tests
# File Created: Monday, 24th August 2020 9:33:07 am
# Author: Dillon Koch
# -----
# Last Modified: Monday, 24th August 2020 10:31:22 am
# Modified By: Dillon Koch
# -----
#
# -----
# Test / QA Testing file for odds team conversions
# ==============================================================================


import json
import os
import sys
from os.path import abspath, dirname
from unittest import TestCase

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Odds.odds_to_db import Odds_to_db


class Test_Odds_Team_Conversions(TestCase):

    def setUp(self):
        pass

    def load_team_conversion_dict(self, league):
        with open(ROOT_PATH + "/Odds/team_conversions.json") as f:
            dic = json.load(f)
        return dic[league]

    def _load_odds_data(self, league):
        o = Odds_to_db(league)
        df = o.load_odds_data()
        return df

    def load_odds_team_keys(self, league):  # Top Level
        odds_df = self._load_odds_data(league)

    def load_odds_team_values(self, league):  # Top Level
        odds_df = self._load_odds_data(league)

    def load_espn_teams(self, league):  # Top Level
        """
        returns a list of all the ESPN team names in the given league
        """
        team_files = os.listdir(ROOT_PATH + "/ESPN_Data/{}/".format(league))
        teams = [team.replace("_", " ").replace('.csv', '') for team in team_files]
        return teams

    def _test_team_keys_in_odds_data(self, team_dict, league):  # QA Testing
        pass

    def _test_odds_teams_in_team_dict(self, team_dict, league):  # QA Testing
        pass

    def _test_team_values_are_espn_teams(self, team_dict, league):  # QA Testing
        """
        making sure values in the team_conversions.json dict are ESPN team names
        - if they're not, there's no ESPN data recorded on this team to merge with
        """
        espn_teams = self.load_espn_teams(league)
        team_values = list(team_dict.values())

        non_espn_teams = [t for t in team_values if t not in espn_teams]
        print(f"{league} non-ESPN teams: {non_espn_teams}")

        # for team in team_values:
        #     assert team in espn_teams, f"{team} is not in the {league} ESPN team names!"

    def _test_every_espn_team_represented(self, team_dict, league):  # QA Testing
        """
        testing that every ESPN team name for a league is represented in the
        values of the team_conversions.json dict
        - if they're not, we have an ESPN dataset with no odds data to merge with
        """
        espn_teams = self.load_espn_teams(league)
        team_values = list(team_dict.values())

        espn_teams_not_represented = [t for t in espn_teams if t not in team_values]
        print(f"{league} ESPN teams not represented: {espn_teams_not_represented}")

    def run_tests(self, league):
        team_dict = self.load_team_conversion_dict(league)
        self._test_team_values_are_espn_teams(team_dict, league)
        self._test_every_espn_team_represented(team_dict, league)

    def test_nfl(self):  # Run
        self.run_tests("NFL")

    def test_nba(self):  # Run
        self.run_tests("NBA")

    def test_ncaaf(self):  # Run
        self.run_tests("NCAAF")

    def test_ncaab(self):  # Run
        self.run_tests("NCAAB")
