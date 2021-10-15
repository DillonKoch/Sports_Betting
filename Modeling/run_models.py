# ==============================================================================
# File: run_models.py
# Project: allison
# File Created: Wednesday, 13th October 2021 9:51:23 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 13th October 2021 9:51:24 pm
# Modified By: Dillon Koch
# -----
#
# -----
# running models on upcoming games and saving predictions
# ==============================================================================


import os
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_data import Modeling_Data


class Run_Models:
    def __init__(self, league):
        self.league = league
        self.modeling_data = Modeling_Data(league)

    def _create_prediction_df(self, path):  # Specific Helper load_prediction_df
        """
        creates a new prediction_df if it doesn't exist yet
        """
        cols = ['Date', 'Home', "Away", "Model_Type", "Prediction", "Confidence"]
        df = pd.DataFrame(columns=cols)
        df.to_csv(path, index=None)
        return df

    def load_prediction_df(self, bet_type):  # Top Level
        """
        loading the prediction df, possibly creating a new one if necessary
        """
        path = ROOT_PATH + f"/Predictions/{self.league}/{bet_type}.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
        else:
            df = self._create_prediction_df(path)
        return df

    def load_upcoming_game_dicts(self):  # Top Level
        """
        loading all the unplayed games from ESPN Games.csv
        """
        path = ROOT_PATH + f"/Data/ESPN/{self.league}/Games.csv"
        df = pd.read_csv(path)
        upcoming_games = df.loc[df.Final_Status.isnull()]
        upcoming_game_dicts = [{col: val for col, val in zip(list(upcoming_games.columns), df_row)}
                               for df_row in upcoming_games.values.tolist()]
        return upcoming_game_dicts

    def upcoming_game_dict_to_row_dict(self, upcoming_game_dict):  # Top Level
        home = upcoming_game_dict['Home']
        away = upcoming_game_dict['Away']
        date = upcoming_game_dict['Date']
        row_dict = self.modeling_data.upcoming_game_to_row_dict(date, home, away, ['Home_Covered'])
        return row_dict

    def run(self, bet_type):  # Run
        prediction_df = self.load_prediction_df(bet_type)
        upcoming_game_dicts = self.load_upcoming_game_dicts()

        upcoming_row_dicts = []
        for upcoming_game_dict in upcoming_game_dicts:
            upcoming_row_dict = self.upcoming_game_dict_to_row_dict(upcoming_game_dict)
            upcoming_row_dicts.append(upcoming_row_dict)

        return upcoming_game_dicts


if __name__ == '__main__':
    league = "NFL"
    bet_type = "Spread"
    x = Run_Models(league)
    self = x
    df = x.run(bet_type)
