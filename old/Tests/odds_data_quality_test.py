# ==============================================================================
# File: odds_data_quality_test.py
# Project: Tests
# File Created: Tuesday, 25th August 2020 9:26:38 am
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 25th August 2020 9:30:08 am
# Modified By: Dillon Koch
# -----
#
# -----
# Testing that the odds datasets have high quality
# ==============================================================================


import os
import sys
from os.path import abspath, dirname
from unittest import TestCase

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class Test_Odds_Data_Quality(TestCase):

    def setUp(self):
        pass

    def load_league_odds_dfs(self, league):  # Top Level
        league_files = listdir_fullpath(ROOT_PATH + "/Odds/{}".format(league))
        csvs = [f for f in league_files if '.csv' in f]
        dfs = [pd.read_csv(csv) for csv in csvs]
        return dfs

    def test_nfl(self):  # Run
        league = "NFL"
        dfs = self.load_league_odds_dfs(league)
