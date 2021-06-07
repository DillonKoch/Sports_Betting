# ==============================================================================
# File: merge_data.py
# Project: Models
# File Created: Saturday, 12th September 2020 12:49:10 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 12th September 2020 1:08:37 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for merging data to train models
# data included from: ESPN, Odds, ESB, WH
# ==============================================================================

import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Merge_Data:
    def __init__(self, league):
        self.league = league

    def load_espn(self):  # Top Level
        espn_df = pd.read_csv(ROOT_PATH + f"/ESPN/Data/{self.league}.csv")
        return espn_df

    def load_odds(self):  # Top Level
        odds_df = pd.read_csv(ROOT_PATH + f"/Odds/{self.league}.csv")
        keep_cols = ['datetime', 'Home', 'Away',
                     'OU_Open', 'OU_Close', 'OU_2H',
                     'Home_Spread_Open', 'Home_Spread_Close', 'Home_Spread_2H',
                     'Away_Spread_Open', 'Away_Spread_Close', 'Away_Spread_2H',
                     'Home_ML', 'Away_ML']
        return odds_df.loc[:, keep_cols]

    def load_esb(self):  # Top Level
        esb_df = pd.read_csv(ROOT_PATH + f"/ESB/Data/{self.league}/Game_Lines.csv")

    def load_wh(self):  # Top Level
        wh_df = pd.read_csv(ROOT_PATH + f"/WH/Data/{self.league}/Game_Lines.csv")

    def run(self):  # Run
        # read in all the dataframes
        # merge on datetime/home/away
        espn_df = self.load_espn()
        odds_df = self.load_odds()

        full_df = pd.merge(espn_df, odds_df, how='left', left_on=['datetime', 'Home', 'Away'])


if __name__ == '__main__':
    x = Merge_Data("NFL")
    self = x
    # x.run()
