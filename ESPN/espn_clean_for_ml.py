# ==============================================================================
# File: espn_clean_for_ml.py
# Project: ESPN
# File Created: Sunday, 6th September 2020 3:03:57 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 6th September 2020 3:15:19 pm
# Modified By: Dillon Koch
# -----
#
# -----
# file that cleans a league's .csv for ML
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESPN_Clean_For_ML:
    def __init__(self, league):
        self.league = league

    def clean_teams(self):
        pass

    def add_dummies(self, df):  # Top Level
        # Home/Away
        # Network
        dummy_cols = ['Home', 'Away', 'Network']
        dummy_df = pd.get_dummies(df[dummy_cols])
        return dummy_df

    def normalize_col(self, df, col_name):  # Top Level
        pass

    def run(self):  # Run
        # one hot encoding categoricals
        # scale the numeric cols
        # clean TOP col to be # seconds
        # make each row contain the season avg up until that game
        original_df = pd.read_csv(ROOT_PATH + f"/ESPN/Data/{self.league}.csv")


if __name__ == '__main__':
    x = ESPN_Clean_For_ML("NFL")
    self = x
    # x.run()
