# ==============================================================================
# File: alignment_test.py
# Project: Sports_Betting
# File Created: Saturday, 6th June 2020 11:07:57 am
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 6th June 2020 4:13:13 pm
# Modified By: Dillon Koch
# -----
#
#
# -----
# File for testing the alignment of odds data and espn data
# ==============================================================================

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

    def test_remove_preseason(self):
        df_paths = self.x._get_df_paths()
        all_team_dfs = self.x._load_all_team_dfs(df_paths)
        all_team_dfs = [self.x._remove_preseason(df) for df in all_team_dfs]
        nfl_weeks = [item for item in range(1, 18)]

        for df in all_team_dfs:
            week_vals = list(df.Week.value_counts().index)
            count = 0
            for week in nfl_weeks:
                if ((week in week_vals) or (str(week) in week_vals)):
                    count += 1

            self.assertEqual(16, count)
            print('success')

            # print(week_vals)
            # count = 0
            # for item in range(0, 18):
            #     try:
            #         print(item, type(item))
            #         if int(item) in week_vals:
            #             count += 1
            #     except BaseException:
            #         pass

    def test_clean_concat_team_dfs(self):
        pass

    def test_load_espn_data(self):
        pass
