# ==============================================================================
# File: bet.py
# Project: allison
# File Created: Friday, 29th October 2021 11:33:23 am
# Author: Dillon Koch
# -----
# Last Modified: Friday, 29th October 2021 11:33:23 am
# Modified By: Dillon Koch
# -----
#
# -----
# Using models to make bets on upcoming games
# ==============================================================================


import os
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Bet:
    def __init__(self, league):
        self.league = league
        self.df_cols = []

    def load_preds_df(self, bet_type):  # Top Level
        """
        Loading the csv from /Data/Predictions/{self.league}/{bet_type}.csv if it exists, else making one
        """
        path = ROOT_PATH + f"/Data/Predictions/{self.league}/{bet_type}.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
        else:
            df = pd.DataFrame(columns=self.df_cols)
        return df

    def run(self):  # Run
        """
        load data of upcoming games
        for each model, insert data and make predictions
        save predictions to the appropriate file
        """
        preds_df = self.load_preds_df()


if __name__ == '__main__':
    x = Bet()
    self = x
    x.run()
