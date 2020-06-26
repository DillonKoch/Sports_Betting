# ==============================================================================
# File: prep_prod.py
# Project: Modeling
# File Created: Thursday, 25th June 2020 4:36:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 25th June 2020 5:40:19 pm
# Modified By: Dillon Koch
# -----
#
# -----
# This file prepares data from the PROD table for ML
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Prep_Prod:
    def __init__(self, league):
        self.league = league

    @property
    def remove_cols(self):  # Property
        all_leagues = ["ESPN_ID", "Season_x", "Date", "League", "Title", "Game_Time", "scraped_ts"]
        nfl = ["Week"]
        return all_leagues + nfl if self.league == "NFL" else all_leagues

    @property
    def dummy_cols(self):  # Property
        all_leagues = ["Home", "Away"]
        return all_leagues

    def load_prod_df(self):  # Top Level
        df = pd.read_csv(ROOT_PATH + "/PROD/{}_PROD.csv".format(self.league))
        include_cols = [col for col in list(df.columns) if col not in self.remove_cols]
        df = df.loc[:, include_cols]
        return df

    def remove_unplayed(self):  # Top Level
        pass  # FIXME

    def add_dummies(self, df, prod_df):  # Top Level
        for col in self.dummy_cols:
            new_dummy_df = pd.get_dummies(prod_df[col], prefix=col)
            df = pd.concat([df, new_dummy_df], axis=1)
        return df

    def run(self):  # Run
        prod_df = self.load_prod_df()
        df = pd.DataFrame()
        df = self.add_dummies(df, prod_df)

        return df


if __name__ == "__main__":
    x = Prep_Prod("NFL")
    prod_df = x.load_prod_df()
    df = x.run()
