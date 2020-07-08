# ==============================================================================
# File: model.py
# Project: Modeling
# File Created: Monday, 6th July 2020 6:45:05 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 7th July 2020 4:23:27 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for building models to predict one of the target variables in the PROD data
# ==============================================================================


import os
import sys
from os.path import abspath, dirname

import pandas as pd
import tensorflow as tf


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.prep_prod import Prep_Prod

physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)


class Model:
    def __init__(self, league):
        self.league = league

    def _load_local_data(self):  # Specific Helper load_data
        y_data_name = "ml_{}.csv".format(self.league.lower())
        x_data_name = "target_{}.csv".format(self.league.lower())
        files = os.listdir(ROOT_PATH + "/Modeling/")
        if ((y_data_name in files) and (x_data_name in files)):
            df = pd.read_csv(y_data_name)
            target_df = pd.read_csv(x_data_name)
            return df, target_df
        return None, None

    def _clean_data(self, df):
        pass

    def load_data(self, training=True):  # Top Level
        df, target_df = self._load_local_data()
        if ((df is None) or (target_df is None)):
            prep_prod = Prep_Prod(self.league)
            df, target_df = prep_prod.run()

        if training:
            print('here')
            df = df.loc[df['Final_Status'].notnull()]
            target_df = target_df.iloc[:len(df), :]
        return df, target_df

    def add_over_column(self):  # Top Level
        # adds a binary 1/0 col to indicate if the over hit or not
        pass

    def add_home_win_col(self, target_df):  # Top Level
        # adds binary col to indicate if home team wins or not
        target_df["Home_win"] = None

        def add_home_win(row):
            home_score = int(row['Home_Score_x'])
            away_score = int(row['Away_Score_x'])
            home_win = 1 if home_score > away_score else 0
            row['Home_win'] = home_win
            return row
        target_df = target_df.apply(lambda row: add_home_win(row), axis=1)
        return target_df

    def run_score_model(self):  # Run
        df, target_df = self.load_data()
        target_df = self.add_home_win_col(target_df)
        return None

    def run_winner_model(self):  # Run
        pass

    def run_over_under_model(self):  # Run
        pass


if __name__ == "__main__":
    x = Model("NFL")
    self = x
    # x.run_score_model()