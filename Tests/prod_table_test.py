# ==============================================================================
# File: prod_table_test.py
# Project: Tests
# File Created: Thursday, 18th June 2020 1:48:50 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 21st June 2020 7:28:03 am
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
    all_dfs = [nfl_dfs, nba_dfs, ncaaf_dfs, ncaab_dfs]

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
        for all_team_dfs in self.all_dfs:
            self.assertIsInstance(all_team_dfs, list)
            for df in all_team_dfs:
                self.assertIsInstance(df, pd.DataFrame)
                self.assertGreater(len(df), 0)

    def test_add_datetime(self):
        for all_team_dfs, league_ob in zip(self.all_dfs, self.league_obs):
            for df in all_team_dfs:
                df = league_ob._add_datetime(df)

    def test_remove_preseason(self):
        for all_team_dfs, league_ob in zip(self.all_dfs, self.league_obs):
            for df in all_team_dfs:
                df = league_ob._add_datetime(df)
                df = league_ob._remove_preseason(df)
                year = str(int(df.Season[0]))
                start_date = league_ob.season_start_dict[year]
                datetimes = list(df.datetime)
                for dt in datetimes:
                    self.assertGreaterEqual(dt, start_date)

                if league_ob.league == "NFL":
                    wk_1to4_count = 0
                    df_weeks = list(df.Week)
                    for week in df_weeks:
                        if str(week) in list('1234'):
                            wk_1to4_count += 1
                    self.assertLessEqual(wk_1to4_count, 4)

    def test_clean_concat_dfs(self):
        for all_team_dfs, league_ob in zip(self.all_dfs, self.league_obs):
            full_df = league_ob._clean_concat_team_dfs(all_team_dfs)
            self.assertIsInstance(full_df, pd.DataFrame)
            espn_ids = list(full_df.ESPN_ID)
            self.assertEqual(len(full_df), len(set(espn_ids)))

            dts = list(full_df.datetime)
            current_dt = dts[0]
            for dt in dts[1:]:
                self.assertGreaterEqual(dt, current_dt)
                current_dt = dt
