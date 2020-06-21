# ==============================================================================
# File: prod_table_test.py
# Project: Tests
# File Created: Thursday, 18th June 2020 1:48:50 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 20th June 2020 8:10:28 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Testing prod_table.py
# ==============================================================================


import sys
from os.path import abspath, dirname
from unittest import TestCase

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from PROD.prod_table import Prod_Table


class Test_Prod_Table(TestCase):
    nfl = Prod_Table("NFL")
    nfl_df_paths = nfl._get_df_paths()
    nfl_dfs = nfl._load_all_team_dfs(nfl_df_paths)

    nba = Prod_Table("NBA")
    nba_df_paths = nba._get_df_paths()
    nba_dfs = nba._load_all_team_dfs(nba_df_paths)

    ncaaf = Prod_Table("NCAAF")
    ncaaf_df_paths = ncaaf._get_df_paths()
    ncaaf_dfs = ncaaf._load_all_team_dfs(ncaaf_df_paths)

    ncaab = Prod_Table("NCAAB")
    ncaab_df_paths = ncaab._get_df_paths()
    ncaab_dfs = ncaab._load_all_team_dfs(ncaab_df_paths)

    league_obs = [nfl, nba, ncaaf, ncaab]

    def setUp(self):
        pass

    def test_check_table_exists(self):
        for league_ob in self.league_obs:
            exists = league_ob.check_table_exists()
            self.assertIsInstance(exists, bool)

    def test_create_dataframe(self):
        for league_ob in self.league_obs:
            df = league_ob.create_dataframe()
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(league_ob.config["ESPN_cols"], list(df.columns))

    def test_load_prod_df(self):
        for league_ob in self.league_obs:
            if league_ob.check_table_exists():
                df = league_ob.load_prod_df()
                self.assertIsInstance(df, pd.DataFrame)

    def test_get_df_paths(self):
        for league_ob in self.league_obs:
            df_paths = league_ob._get_df_paths()
            self.assertIsInstance(df_paths, list)
            for item in df_paths:
                self.assertIsInstance(item, str)

    def test_load_all_team_dfs(self):
        for all_team_dfs in [self.nfl_dfs, self.nba_dfs, self.ncaaf_dfs, self.ncaab_dfs]:
            self.assertIsInstance(all_team_dfs, list)
            for df in all_team_dfs:
                self.assertIsInstance(df, pd.DataFrame)
                self.assertGreater(len(df), 0)

    def test_remove_preseason(self):
        pass
