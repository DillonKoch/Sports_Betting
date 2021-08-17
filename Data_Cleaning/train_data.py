# ==============================================================================
# File: train_data.py
# Project: allison
# File Created: Tuesday, 17th August 2021 1:35:59 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 17th August 2021 1:36:01 pm
# Modified By: Dillon Koch
# -----
#
# -----
# preparing training data for any ML modeline
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Train_Data:
    def __init__(self, league):
        self.league = league
        self.espn_games_df = self.load_espn_games()
        self.espn_cols = list(self.espn_games_df.columns) + ['Home_Win']
        self.odds_cols = []
        self.esb_cols = []

    def run(self, features, targets):  # Run
        # load, merge necessary datasets
        # specify target col, input cols

        # return y label, x training data
        # option to split into train/cv/test here in this class
        pass


if __name__ == '__main__':
    league = "NFL"
    x = Train_Data(league)
    self = x

    features = ['Home_Final', 'Away_Final']
    targets = ['Home_Win']
    x.run(features, targets)
