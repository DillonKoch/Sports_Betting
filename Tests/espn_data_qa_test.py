# ==============================================================================
# File: espn_data_qa_test.py
# Project: Tests
# File Created: Sunday, 6th September 2020 3:16:58 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 6th September 2020 6:13:36 pm
# Modified By: Dillon Koch
# -----
#
# -----
# testing to be sure the ESPN data is clean
# ==============================================================================


import json
import re
import sys
import warnings
from os.path import abspath, dirname
from unittest import TestCase

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Test_ESPN_Data_Quality(TestCase):

    def setUp(self):
        warnings.filterwarnings('ignore')
        self.leagues = ["NFL", "NBA", "NCAAF", "NCAAB"]

    def load_data(self, league):
        df = pd.read_csv(ROOT_PATH + f"/ESPN/Data/{league}.csv")
        return df

    def _run_espn_id_test(self, df):  # Specific Helper test_espn_id
        """
        all ESPN_ID's must be integers and have 9 digits
        """
        espn_ids = list(df['ESPN_ID'])
        for espn_id in espn_ids:
            self.assertIsInstance(espn_id, int)
            self.assertEqual(9, len(str(espn_id)))

    def test_espn_id(self):  # Top Level
        for league in self.leagues:
            df = self.load_data(league)
            self._run_espn_id_test(df)

    def _run_season_test(self, df):  # Specific Helper test_season
        """
        season values must be int, four digits, >= 2007
        """
        seasons = list(df['Season'])
        for season in seasons:
            self.assertIsInstance(season, int)
            self.assertEqual(4, len(str(season)))
            self.assertGreaterEqual(season, 2007)

    def test_season(self):  # Top Level
        for league in self.leagues:
            df = self.load_data(league)
            self._run_season_test(df)

    def _run_date_test(self, df):  # Specific Helper test_date
        date_comp = re.compile(
            r"^(January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}$")

        dates = list(df['Date'])
        for date in dates:
            self.assertIsInstance(date, str)
            match = re.match(date_comp, date)
            self.assertIsNotNone(match)

    def test_date(self):  # Top Level
        for league in self.leagues:
            df = self.load_data(league)
            self._run_date_test(df)

    def _run_team_names_test(self, df, league):  # Specific Helper test_team_names
        home_teams = list(df['Home'])
        away_teams = list(df['Away'])
        all_teams = home_teams + away_teams
        all_teams = list(set(all_teams))

        with open(ROOT_PATH + "/Utility/current_teams.json", 'r') as f:
            current_teams = json.load(f)
        current_teams = current_teams[league]

        for team in all_teams:
            assert team in current_teams, f"{team} not in current teams for {league}"

    def test_team_names(self):  # Top Level
        for league in ["NFL", "NBA"]:
            df = self.load_data(league)
            self._run_team_names_test(df, league)

    def _run_records_test(self, df):  # Specific Helper test_records
        home_records = list(df['Home_Record'])
        away_records = list(df['Away_Record'])
        all_records = home_records + away_records

        for record in all_records:
            self.assertIsInstance(record, str)

    def test_records(self):  # Top Level
        for league in self.leagues:
            df = self.load_data(league)
            if "NCAA" in league:
                df = df.loc[df.Home_Record.notnull()]
                df = df.loc[df.Away_Record.notnull()]
            self._run_records_test(df)
