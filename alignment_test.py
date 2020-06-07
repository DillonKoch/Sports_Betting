# ==============================================================================
# File: alignment_test.py
# Project: Sports_Betting
# File Created: Saturday, 6th June 2020 11:07:57 am
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 7th June 2020 7:44:47 am
# Modified By: Dillon Koch
# -----
#
#
# -----
# File for testing the alignment of odds data and espn data
# ==============================================================================

import datetime
import sys
from os.path import abspath, dirname
from unittest import TestCase

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from alignment import Alignment


class Test_Alignment(TestCase):
    x = Alignment("NFL")

    def setUp(self):
        pass

    def test_teams(self):
        self.assertEqual(32, len(self.x.teams))
        for item in self.x.teams:
            self.assertIsInstance(item, str)

    def test_odds_conversion_dict(self):
        cd = self.x.odds_conversion_dict
        self.assertEqual(36, len(list(cd.keys())))

    def test_get_df_paths(self):
        df_paths = self.x._get_df_paths()

        for item in df_paths:
            self.assertTrue('.csv' in item)
            self.assertTrue(int(item[-8:-4]) > 2006)

    def test_load_all_team_dfs(self):
        df_paths = self.x._get_df_paths()
        all_team_dfs = self.x._load_all_team_dfs(df_paths)

        for df in all_team_dfs:
            self.assertIsInstance(df, pd.DataFrame)

        self.assertEqual(len(df_paths), len(all_team_dfs))

    def test_add_datetime(self):
        df_paths = self.x._get_df_paths()
        all_team_dfs = self.x._load_all_team_dfs(df_paths)
        test_df = all_team_dfs[0]
        test_df = self.x._add_datetime(test_df)

        self.assertTrue("datetime" in list(test_df.columns))
        for item in list(test_df.datetime):
            self.assertIsInstance(item, datetime.date)

    def test_remove_preseason(self):
        df_paths = self.x._get_df_paths()
        all_team_dfs = self.x._load_all_team_dfs(df_paths)
        all_team_dfs = [self.x._add_datetime(df) for df in all_team_dfs]
        all_team_dfs = [self.x._remove_preseason(df) for df in all_team_dfs]

        nfl_weeks = [str(item) for item in list(range(1, 18))]
        for df in all_team_dfs:
            count = 0
            week_vals = list(df.Week)
            for item in week_vals:
                if str(item) in nfl_weeks:
                    count += 1
            self.assertEqual(16, count)

    def test_clean_concat_team_dfs(self):
        df_paths = self.x._get_df_paths()
        all_team_dfs = self.x._load_all_team_dfs(df_paths)
        all_team_dfs = [self.x._add_datetime(df) for df in all_team_dfs]
        all_team_dfs = [self.x._remove_preseason(df) for df in all_team_dfs]
        full_df = self.x._clean_concat_team_dfs(all_team_dfs)

        self.assertIsInstance(full_df, pd.DataFrame)

    def test_load_espn_data(self):
        espn_df = self.x.load_espn_data()
        self.assertIsInstance(espn_df, pd.DataFrame)

    def test_load_odds_data(self):
        odds_df = self.x.load_odds_data()
        self.assertIsInstance(odds_df, pd.DataFrame)
        self.assertEqual(6942, odds_df.shape[0])
        self.assertEqual(14, odds_df.shape[1])

    def test_convert_odds_teams(self):
        odds_df = self.x.load_odds_data()
        odds_df = self.x.convert_odds_teams(odds_df)
        team_names = list(self.x.odds_conversion_dict.values())
        for item in list(odds_df.Team):
            self.assertIn(item, team_names)

    def test_convert_odds_date(self):
        odds_df = self.x.load_odds_data()
        odds_df = self.x.convert_odds_teams(odds_df)
        odds_df = self.x.convert_odds_date(odds_df)
        self.assertEqual(17, odds_df.shape[1])

    def test_game_pairs_from_odds(self):
        odds_df = self.x.load_odds_data()
        odds_df = self.x.convert_odds_teams(odds_df)
        odds_df = self.x.convert_odds_date(odds_df)
        game_pairs = self.x.game_pairs_from_odds(odds_df)

        for item in game_pairs:
            self.assertEqual(2, len(item))
            for subitem in item:
                self.assertIsInstance(subitem, pd.Series)

    def test_get_line_ou_from_game_pairs(self):
        odds_df = self.x.load_odds_data()
        odds_df = self.x.convert_odds_teams(odds_df)
        odds_df = self.x.convert_odds_date(odds_df)
        game_pairs = self.x.game_pairs_from_odds(odds_df)

        for pair in game_pairs:
            row1, row2 = pair
            home_row = row1 if row1['VH'] in ["H", "N"] else row2
            away_row = row1 if row1['VH'] == 'V' else row2
            cols = ["Open", "Close", "2H"]
            for col in cols:
                over_under, home_line, away_line = self.x._get_line_ou_from_2rows(home_row, away_row, col)
                self.assertTrue(over_under > float(home_line[1:]))
                self.assertTrue(over_under > float(away_line[1:]))
