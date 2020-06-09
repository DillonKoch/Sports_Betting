# ==============================================================================
# File: alignment_test.py
# Project: Sports_Betting
# File Created: Saturday, 6th June 2020 11:07:57 am
# Author: Dillon Koch
# -----
# Last Modified: Monday, 8th June 2020 5:04:32 pm
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
    nfl = Alignment("NFL")
    nba = Alignment("NBA")
    ncaaf = Alignment("NCAAF")
    ncaab = Alignment("NCAAB")
    league_obs = [nfl, nba]

    def setUp(self):
        pass

    def test_init(self):  # Top Level
        self.assertEqual("nfl_alignment.json", self.nfl.config_filename)
        self.assertEqual("nba_alignment.json", self.nba.config_filename)
        self.assertEqual("ncaaf_alignment.json", self.ncaaf.config_filename)
        self.assertEqual("ncaab_alignment.json", self.ncaab.config_filename)

    def test_teams(self):  # Top Level
        self.assertEqual(32, len(self.nfl.teams))
        self.assertEqual(30, len(self.nba.teams))

        for item in self.nfl.teams:
            self.assertIsInstance(item, str)
        for item in self.nba.teams:
            self.assertIsInstance(item, str)

    def _season_start_test(self, league_ob):  # Specific Helper
        league_dict = league_ob.season_start_dict
        for item in list(league_dict.values()):
            self.assertIsInstance(item, datetime.date)
        seasons = [str(item) for item in range(2007, 2020)]
        self.assertEqual(seasons, list(league_dict.keys()))

    def test_season_start_dict(self):  # Top Level
        for league_ob in self.league_obs:
            self._season_start_test(league_ob)

    def _get_df_paths_test(self, league_ob):  # Specific Helper
        df_paths = league_ob._get_df_paths()
        for item in df_paths:
            self.assertTrue('.csv' in item)
            self.assertTrue(int(item[-8:-4]) > 2006)

    def test_get_df_paths(self):  # Top Level
        for league_ob in self.league_obs:
            self._get_df_paths_test(league_ob)

    def _load_all_team_dfs_test(self, league_ob):  # Specific Helper
        df_paths = league_ob._get_df_paths()
        all_team_dfs = league_ob._load_all_team_dfs(df_paths)
        for df in all_team_dfs:
            self.assertIsInstance(df, pd.DataFrame)
        self.assertEqual(len(df_paths), len(all_team_dfs))

    def test_load_all_team_dfs(self):  # Top Level
        for league_ob in self.league_obs:
            self._load_all_team_dfs_test(league_ob)

    def _add_datetime_test(self, league_ob):  # Specific Helper
        df_paths = league_ob._get_df_paths()
        all_team_dfs = league_ob._load_all_team_dfs(df_paths)
        test_df = all_team_dfs[0]
        test_df = league_ob._add_nfl_datetime(test_df) if league_ob.league == "NFL" else league_ob._add_datetime(test_df)
        self.assertTrue("datetime" in list(test_df.columns))
        for item in list(test_df.datetime):
            self.assertIsInstance(item, datetime.date)

    def test_add_datetime(self):  # Top Level
        for league_ob in self.league_obs:
            self._add_datetime_test(league_ob)

    # def test_remove_preseason(self):
    #     df_paths = self.nfl._get_df_paths()
    #     all_team_dfs = self.nfl._load_all_team_dfs(df_paths)
    #     all_team_dfs = [self.nfl._add_datetime(df) for df in all_team_dfs]
    #     all_team_dfs = [self.nfl._remove_preseason(df) for df in all_team_dfs]

    #     nfl_weeks = [str(item) for item in list(range(1, 18))]
    #     for df in all_team_dfs:
    #         count = 0
    #         week_vals = list(df.Week)
    #         for item in week_vals:
    #             if str(item) in nfl_weeks:
    #                 count += 1
    #         self.assertEqual(16, count)

    # def test_clean_concat_team_dfs(self):
    #     df_paths = self.nfl._get_df_paths()
    #     all_team_dfs = self.nfl._load_all_team_dfs(df_paths)
    #     all_team_dfs = [self.nfl._add_datetime(df) for df in all_team_dfs]
    #     all_team_dfs = [self.nfl._remove_preseason(df) for df in all_team_dfs]
    #     full_df = self.nfl._clean_concat_team_dfs(all_team_dfs)

    #     self.assertIsInstance(full_df, pd.DataFrame)

    # def test_load_espn_data(self):
    #     espn_df = self.nfl.load_espn_data()
    #     self.assertIsInstance(espn_df, pd.DataFrame)

    # def test_load_odds_data(self):
    #     odds_df = self.nfl.load_odds_data()
    #     self.assertIsInstance(odds_df, pd.DataFrame)
    #     self.assertEqual(6942, odds_df.shape[0])
    #     self.assertEqual(14, odds_df.shape[1])

    # def test_convert_odds_teams(self):
    #     odds_df = self.nfl.load_odds_data()
    #     odds_df = self.nfl.convert_odds_teams(odds_df)
    #     team_names = list(self.nfl.odds_conversion_dict.values())
    #     for item in list(odds_df.Team):
    #         self.assertIn(item, team_names)

    # def test_convert_odds_date(self):
    #     odds_df = self.nfl.load_odds_data()
    #     odds_df = self.nfl.convert_odds_teams(odds_df)
    #     odds_df = self.nfl.convert_odds_date(odds_df)
    #     self.assertEqual(17, odds_df.shape[1])

    # def test_game_pairs_from_odds(self):
    #     odds_df = self.nfl.load_odds_data()
    #     odds_df = self.nfl.convert_odds_teams(odds_df)
    #     odds_df = self.nfl.convert_odds_date(odds_df)
    #     game_pairs = self.nfl.game_pairs_from_odds(odds_df)

    #     for item in game_pairs:
    #         self.assertEqual(2, len(item))
    #         for subitem in item:
    #             self.assertIsInstance(subitem, pd.Series)

    # def test_get_line_ou_from_game_pairs(self):
    #     odds_df = self.nfl.load_odds_data()
    #     odds_df = self.nfl.convert_odds_teams(odds_df)
    #     odds_df = self.nfl.convert_odds_date(odds_df)
    #     game_pairs = self.nfl.game_pairs_from_odds(odds_df)

    #     for pair in game_pairs:
    #         row1, row2 = pair
    #         home_row = row1 if row1['VH'] in ["H", "N"] else row2
    #         away_row = row1 if row1['VH'] == 'V' else row2
    #         cols = ["Open", "Close", "2H"]
    #         for col in cols:
    #             over_under, home_line, away_line = self.nfl._get_line_ou_from_2rows(home_row, away_row, col)
    #             self.assertTrue(over_under > float(home_line[1:]))
    #             self.assertTrue(over_under > float(away_line[1:]))
