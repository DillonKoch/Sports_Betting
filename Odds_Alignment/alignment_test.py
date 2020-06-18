# ==============================================================================
# File: alignment_test.py
# Project: Sports_Betting
# File Created: Saturday, 6th June 2020 11:07:57 am
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 13th June 2020 6:49:56 pm
# Modified By: Dillon Koch
# -----
#
#
# -----
# File for testing the alignment of odds data and espn data
# ==============================================================================

import copy
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
    league_obs = [nfl, nba, ncaaf, ncaab]

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
            self.assertTrue(int(item[-8:-4]) > 2007)

    def test_get_df_paths(self):  # Top Level
        for league_ob in self.league_obs:
            self._get_df_paths_test(league_ob)

    def _load_all_team_dfs_test(self, league_ob):  # Specific Helper
        df_paths = league_ob._get_df_paths()
        all_team_dfs = league_ob._load_all_team_dfs(df_paths)
        for df in all_team_dfs:
            self.assertIsInstance(df, pd.DataFrame)
        self.assertTrue(len(df_paths) >= len(all_team_dfs))

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

    def test_remove_preseason(self):
        df_paths = self.nfl._get_df_paths()
        all_team_dfs = self.nfl._load_all_team_dfs(df_paths)
        all_team_dfs = [self.nfl._add_datetime(df) for df in all_team_dfs]
        all_team_dfs = [self.nfl._remove_preseason(df) for df in all_team_dfs]

        nfl_weeks = [str(item) for item in list(range(1, 18))]
        for df in all_team_dfs:
            count = 0
            week_vals = list(df.Week)
            for item in week_vals:
                if str(item) in nfl_weeks:
                    count += 1
            self.assertEqual(16, count)

    def _clean_concat_team_dfs_test(self, league_ob):  # Specific Helper test_clean_concat_team_dfs
        df_paths = league_ob._get_df_paths()
        all_team_dfs = league_ob._load_all_team_dfs(df_paths)
        all_team_dfs = [league_ob._remove_preseason(df) for df in all_team_dfs]
        all_team_dfs = [league_ob._add_datetime(df) for df in all_team_dfs]
        espn_df = league_ob._clean_concat_team_dfs(all_team_dfs)

        self.assertIsInstance(espn_df, pd.DataFrame)
        self.assertEqual(list(all_team_dfs[0].columns), list(espn_df.columns))

        total_team_df_len = sum([len(df) for df in all_team_dfs])
        espn_df_len = len(espn_df)
        self.assertGreater(total_team_df_len, espn_df_len)

    def test_clean_concat_team_dfs(self):  # Top Level
        for league_ob in self.league_obs:
            self._clean_concat_team_dfs_test(league_ob)

    def _load_espn_data_test(self, league_ob):  # Specific Helper test_load_espn_data
        espn_df = league_ob.load_espn_data()
        self.assertIsInstance(espn_df, pd.DataFrame)
        cols = [
            "ESPN_ID",
            "Season",
            "Date",
            "Home",
            "Away",
            "Home_Record",
            "Away_Record",
            "Home_Score",
            "Away_Score",
            "Line",
            "Over_Under",
            "Final_Status",
            "Network",
            "HOT",
            "AOT",
            "League"]
        for col in cols:
            self.assertIn(col, list(espn_df.columns))

    def test_load_espn_data(self):  # Top Level
        for league_ob in self.league_obs:
            self._load_espn_data_test(league_ob)

    def _load_odds_data_test(self, league_ob):  # Specific Helper
        odds_df = league_ob.load_odds_data()
        self.assertIsInstance(odds_df, pd.DataFrame)
        if league_ob.league != "NCAAB":
            self.assertEqual(14, odds_df.shape[1])
        else:
            self.assertEqual(12, odds_df.shape[1])

    def test_load_odds_data(self):  # Top Level
        for league_ob in self.league_obs:
            self._load_odds_data_test(league_ob)

    def _convert_odds_teams_test(self, league_ob):  # Specific Helper test_convert_odds_teams
        odds_df = league_ob.load_odds_data()
        new_odds_df = league_ob.convert_odds_teams(odds_df)

        self.assertEqual(odds_df.shape, new_odds_df.shape)

    def test_convert_odds_teams(self):  # Top Level
        for league_ob in self.league_obs:
            self._convert_odds_teams_test(league_ob)

    def _convert_odds_date_test(self, league_ob):  # Specific Helper
        odds_df = league_ob.load_odds_data()
        odds_df = league_ob.convert_odds_teams(odds_df)
        new_odds_df = league_ob.convert_odds_date(copy.deepcopy(odds_df))

        self.assertTrue(new_odds_df.shape[1] == odds_df.shape[1] + 3)
        new_cols = ['datetime', 'month', 'day']
        for col in new_cols:
            self.assertIn(col, list(new_odds_df.columns))

    def test_convert_odds_date(self):  # Top Level
        for league_ob in self.league_obs:
            self._convert_odds_date_test(league_ob)

    def _game_pairs_from_odds_test(self, league_ob):  # Specific Helper test_game_pairs_from_odds
        odds_df = league_ob.load_odds_data()
        odds_df = league_ob.convert_odds_teams(odds_df)
        odds_df = league_ob.convert_odds_date(odds_df)
        game_pairs = league_ob.game_pairs_from_odds(odds_df)

        for pair in game_pairs:
            self.assertEqual(2, len(pair))
            for subitem in pair:
                self.assertIsInstance(subitem, pd.Series)

    def test_game_pairs_from_odds(self):  # Top Level
        for league_ob in self.league_obs:
            self._game_pairs_from_odds_test(league_ob)

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
