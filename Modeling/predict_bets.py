# ==============================================================================
# File: predict_bets.py
# Project: Modeling
# File Created: Monday, 13th July 2020 1:36:54 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 14th July 2020 4:53:25 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# File for running all the models in a league to make predictions, saving to Results folder
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd
import tensorflow as tf
from tensorflow import keras

physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Predict_Bets:
    def __init__(self, league: str):
        self.league = league

    def create_results_df(self):  # Top Level
        cols = ["ESPN_ID", "Season", "Date", "Home", "Away", "Home_Record", "Away_Record", "Network",
                "Title", "Game_Time", "Over_ESB", "Over_ml_ESB", ]
        df = pd.DataFrame(columns=cols)
        return df

    def load_upcoming_games(self):  # Top Level
        """
        Returns a df with unfinished games that have odds from Elite Sportsbook
        """
        prod_path = ROOT_PATH + "/PROD/{}_PROD.csv".format(self.league.upper())
        df = pd.read_csv(prod_path)
        df = df.loc[df.Final_Status.isnull(), :]
        df = df.loc[df['Over_ESB'].notnull() | df['Home_Line_ESB'].notnull() | df['Home_Line_ESB'].notnull()]
        return df

    def _load_models(self):  # Specific Helper predict_upcoming_games
        # self.model_OU = keras.models.load_model(ROOT_PATH + "/Models/{}/{}_OU.h5".format(self.league, self.league))
        score_model = keras.models.load_model(ROOT_PATH + "/Models/{}/{}_Score.h5".format(self.league, self.league))
        return score_model

    def _predict_score(self, game):  # Specific Helper predict_upcoming_games
        pass

    def _predict_OU(self, game):  # Specific Helper predict_upcoming_games
        pass

    def predict_upcoming_games(self, df):  # Top Level
        score_model = self._load_models()

    def create_df(self):  # Top Level
        pass

    def run(self):  # Run
        upcoming_games = self.load_upcoming_games()


if __name__ == "__main__":
    x = Predict_Bets("NFL")
    self = x
