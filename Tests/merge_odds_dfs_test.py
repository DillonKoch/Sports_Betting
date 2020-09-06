# ==============================================================================
# File: merge_odds_dfs_test.py
# Project: Tests
# File Created: Thursday, 3rd September 2020 4:51:55 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 3rd September 2020 8:35:11 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Testing the merge_odds_dfs function used by ESB and WH scrapers
# ==============================================================================

import sys
from os.path import abspath, dirname
from unittest import TestCase

import pandas as pd
import datetime


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.merge_odds_dfs import merge_odds_dfs, _split_old_df


class Test_Merge_Odds_Dfs(TestCase):

    def setUp(self):
        self.df1 = pd.read_csv("odds_test_data1.csv")
        self.df2 = pd.read_csv("odds_test_data2.csv")
        self.drop_cols = ["datetime", "Home", "Away"]

    def test_setup(self):
        # types are pd.DataFrame
        self.assertIsInstance(self.df1, pd.DataFrame)
        self.assertIsInstance(self.df2, pd.DataFrame)

        # accurate lengths
        self.assertEqual(16, len(self.df1))
        self.assertEqual(12, len(self.df2))

        # same column names
        self.assertEqual(list(self.df1.columns), list(self.df2.columns))

    def test_split_old_df(self):
        """
        testing to be sure the _split_old_df function works, and that the
        two df's combined are equal to the original
        """
        locked_df, newest_df = _split_old_df(self.df1, self.drop_cols)

        re_merged_df = pd.concat([locked_df, newest_df])
        self.assertEqual(len(self.df1), len(re_merged_df))

    def _count_pats_dolphins_rows(self, df):
        pd_df = df.loc[df.Home == "New England Patriots"]
        pd_df = pd_df.loc[pd_df.Away == "Miami Dolphins"]
        return len(pd_df)

    def test_patriots_dolphins(self):
        """
        df1 has an original pats-dolphins odds row, then a newly updated one,
        then df2 has the original odds row back with a new scraped_ts (simulating the odds
        changing back to where they were before - want to keep these rows), testing to
        be sure the merged df3 has all 3 of these rows
        """
        df1_pats_dolphins = self._count_pats_dolphins_rows(self.df1)
        self.assertEqual(2, df1_pats_dolphins)

        df2_pats_dolphins = self._count_pats_dolphins_rows(self.df2)
        self.assertEqual(1, df2_pats_dolphins)

        odds_cols = ['Home', 'Away', 'Home_ML', 'Away_ML', 'Home_Line', 'Away_Line']
        df3 = merge_odds_dfs(self.df1, self.df2, self.drop_cols, odds_cols)
        df3_pats_dolphins = self._count_pats_dolphins_rows(df3)
        self.assertEqual(3, df3_pats_dolphins)
