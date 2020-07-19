# ==============================================================================
# File: predict_bets.py
# Project: Modeling
# File Created: Monday, 13th July 2020 1:36:54 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 18th July 2020 5:17:49 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# File for running all the models in a league to make predictions, saving to Results folder
# ==============================================================================


import sys
from os.path import abspath, dirname
from numpy.core.numeric import full

import pandas as pd
import tensorflow as tf
import numpy as np
from tensorflow import keras

physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from model import Model


class Predict_Bets:
    def __init__(self, league: str):
        self.league = league
        self.model = Model(self.league)
        self.pred_df_path = ROOT_PATH + "/Results/{}_Results.csv".format(self.league)

    def load_upcoming_games(self):  # Top Level
        """
        Returns a df with unfinished games that have odds from Elite Sportsbook
        """
        prod_path = ROOT_PATH + "/PROD/{}_PROD.csv".format(self.league.upper())
        df = pd.read_csv(prod_path)
        df = df.loc[df.Final_Status.isnull(), :]
        df = df.loc[df['Over_ESB'].notnull() | df['Home_Line_ESB'].notnull() | df['Home_Line_ESB'].notnull()]
        return df

    def create_results_df(self, upcoming_games):  # Top Level
        cols = ["ESPN_ID", "Season_x", "datetime", "Home", "Away", "Home_Record", "Away_Record", "Network",
                "Title", "Game_Time", "Home_ML_ESB", "Away_ML_ESB", "Pred_Home_win",
                "Home_Line_ESB", "Home_Line_ml_ESB", "Away_Line_ESB", "Away_Line_ml_ESB", "Pred_Home_Score",
                "Pred_Away_Score"]
        df = pd.DataFrame(columns=cols)
        for col in cols:
            df[col] = upcoming_games[col] if col in list(upcoming_games.columns) else None
        df.reset_index(drop=True, inplace=True)
        return df

    def _load_model(self, name):  # Global Helper
        model_path = ROOT_PATH + "/Models/{}/{}".format(self.league, name)
        model = keras.models.load_model(model_path)
        return model

    def predict_home_win(self, df, ml_df):  # Top Level
        model = self._load_model("{}_Home_Win.h5".format(self.league))
        for i, row in df.iterrows():
            ESPN_ID = row['ESPN_ID']
            X_data = ml_df.loc[ml_df.ESPN_ID == ESPN_ID, :]
            X_data = self.model.remove_non_ml_cols(X_data)
            X_data = np.array(X_data)
            pred = model.predict([X_data])
            row['Pred_Home_win'] = round(pred[0][0] * 100, 1)
            df.iloc[i, :] = row
        return df

    def predict_score(self, df, ml_df):  # Top Level
        model = self._load_model("{}_Predict_Score.h5".format(self.league))
        for i, row in df.iterrows():
            ESPN_ID = row['ESPN_ID']
            X_data = ml_df.loc[ml_df.ESPN_ID == ESPN_ID, :]
            X_data = self.model.remove_non_ml_cols(X_data)
            X_data = np.array(X_data)
            preds = model.predict([X_data])
            row['Pred_Home_Score'] = preds[0][0]
            row['Pred_Away_Score'] = preds[0][1]
            df.iloc[i, :] = row

        return df

    def create_new_pred_df(self, ml_df, upcoming_games):  # Run
        df = self.create_results_df(upcoming_games)
        df = self.predict_home_win(df, ml_df)
        df = self.predict_score(df, ml_df)
        return df

    def load_existing_pred_df(self):  # Top Level
        try:
            pred_df = pd.read_csv(self.pred_df_path)
            return pred_df
        except FileNotFoundError:
            print("Pred df does not exist, making a new one...")
            return None

    def run(self, run_msg=None):  # Run
        upcoming_games = self.load_upcoming_games()
        ml_df, target_df = self.model.load_data(training=False)
        new_pred_df = self.create_new_pred_df(ml_df, upcoming_games)
        existing_pred_df = self.load_existing_pred_df()

        if existing_pred_df is None:
            new_pred_df.to_csv(self.pred_df_path, index=False)
            return new_pred_df

        full_pred_df = pd.concat([existing_pred_df, new_pred_df])
        full_pred_df.drop_duplicates(keep="last", inplace=True)
        full_pred_df.to_csv(self.pred_df_path, index=False)
        return full_pred_df


if __name__ == "__main__":
    x = Predict_Bets("NFL")
    self = x
    df = x.run()
