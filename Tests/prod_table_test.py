# ==============================================================================
# File: prod_table_test.py
# Project: Tests
# File Created: Thursday, 18th June 2020 1:48:50 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 18th June 2020 4:56:55 pm
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
    nba = Prod_Table("NBA")
    ncaaf = Prod_Table("NCAAF")
    ncaab = Prod_Table("NCAAB")
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

    def test_load_prod_df(self):
        for league_ob in self.league_obs:
            if league_ob.check_table_exists():
                df = league_ob.load_prod_df()
                self.assertIsInstance(df, pd.DataFrame)

    def test_get_espn_paths(self):
        for league_ob in self.league_obs:
            df_paths = league_ob._get_espn_paths()
            self.assertIsInstance(df_paths, list)
            for item in df_paths:
                self.assertIsInstance(item, str)

    def test_load_concat_espn_paths(self):
        for league_ob in self.league_obs:
            df_paths = league_ob._get_espn_paths()
            df = league_ob._load_concat_espn_paths(df_paths)
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(league_ob.config["ESPN_cols"], list(df.columns))
            print(league_ob.league, "Success")

    def test_remove_preseason(self):
        pass
