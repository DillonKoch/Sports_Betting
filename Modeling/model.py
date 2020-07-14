# ==============================================================================
# File: model.py
# Project: Modeling
# File Created: Monday, 6th July 2020 6:45:05 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 13th July 2020 1:15:38 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for building models to predict one of the target variables in the PROD data
# ==============================================================================


import os
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
import tensorflow as tf
import wandb
from wandb.keras import WandbCallback
from tensorflow import keras


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.prep_prod import Prep_Prod

physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

wandb.init(project="sports-betting")


class Model:
    """
    class for creating models to predict one of the target variables in the PROD df
    """

    def __init__(self, league: str):
        self.league = league

    def _load_local_data(self):  # Specific Helper load_data
        y_data_name = "{}_ml.csv".format(self.league.lower())
        x_data_name = "{}_target.csv".format(self.league.lower())
        files = os.listdir(ROOT_PATH + "/Modeling/")
        if ((y_data_name in files) and (x_data_name in files)):
            print("using locally saved training/target data")
            df = pd.read_csv(y_data_name)
            target_df = pd.read_csv(x_data_name)
            return df, target_df
        return None, None

    def load_data(self, training=True):  # Top Level
        df, target_df = self._load_local_data()
        if ((df is None) or (target_df is None)):
            prep_prod = Prep_Prod(self.league)
            df, target_df = prep_prod.run()

        if training:
            print('using training data')
            df = df.loc[df['Final_Status'].notnull()]
            target_df = target_df.iloc[:len(df), :]
        return df, target_df

    def oversample_even_classes(self, df, target_col):  # Top Level
        target_vals = list(set(list(df[target_col])))
        sample_num = max([len(df.loc[df[target_col] == val]) for val in target_vals])

        oversampled_df = pd.DataFrame(columns=list(df.columns))
        for val in target_vals:
            new_df = df.loc[df[target_col] == val]
            new_df = new_df.sample(sample_num, replace=True)
            oversampled_df = pd.concat([oversampled_df, new_df])
        oversampled_df = oversampled_df.sample(frac=1)
        return oversampled_df

    def save_model(self, model, name):  # Top Level
        path = ROOT_PATH + "/Models/{}/{}".format(self.league, name)
        path = path + ".h5" if ".h5" not in path else path
        model.save(path)
        print("Model saved to {}!".format(path))


class Score_Model(Model):
    """
    class for predicting the winner of a game
    """

    def home_win_model(self):  # Top Level
        model = keras.Sequential([
            keras.layers.Dense(256, input_shape=([149]), activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid'),
        ])

        opt = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=opt,
                      loss="binary_crossentropy",
                      metrics=['accuracy'])
        return model

    def get_home_win_col(self, target_df):  # Top Level
        """
        adds binary col to indicate if home team wins or not
        """
        target_df["Home_win"] = None

        def add_home_win(row):
            home_score = int(row['Home_Score_x'])
            away_score = int(row['Away_Score_x'])
            home_win = 1 if home_score > away_score else 0
            row['Home_win'] = home_win
            return row
        target_df = target_df.apply(lambda row: add_home_win(row), axis=1)
        return target_df['Home_win']

    def run_score_model(self):  # Run
        df, target_df = self.load_data()
        home_win_col = self.get_home_win_col(target_df)
        full_df = pd.concat([df, home_win_col], axis=1)
        full_df = full_df.dropna(axis=0)
        full_df = self.oversample_even_classes(full_df, "Home_win")

        X_cols = [item for item in list(df.columns) if item not in ["Final_Status", "datetime", "Home_win"]]
        X_data = full_df.loc[:, X_cols]
        y_data = full_df.loc[:, 'Home_win']

        X_data = np.array(X_data).astype(float)
        y_data = np.array(y_data).astype(int)

        model = self.home_win_model()
        model.fit([X_data], y_data, epochs=30, batch_size=16, callbacks=[WandbCallback(data_type="data", labels=y_data)])
        model.save("{}_Score.h5".format(self.league))
        return model

    def predict_score_model(self):  # Top Level
        model = keras.Sequential([
            keras.layers.Dense(256, input_shape=([149]), activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(2, activation='linear')
        ])
        opt = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=opt,
                      loss="mse",
                      metrics=['accuracy'])
        return model

    def run_predict_score(self):  # Run
        df, target_df = self.load_data()
        score_df = target_df.loc[:, ["Home_Score_x", "Away_Score_x"]]
        full_df = pd.concat([df, score_df], axis=1)
        full_df = full_df.dropna(axis=0)

        X_cols = [item for item in list(df.columns) if item not in
                  ["Final_Status", "datetime", "Home_Score", "Away_Score"]]
        X_data = full_df.loc[:, X_cols]
        y_data = full_df.loc[:, ["Home_Score_x", "Away_Score_x"]]

        X_data = np.array(X_data).astype(float)
        y_data = np.array(y_data).astype(float)

        model = self.predict_score_model()
        model.fit(X_data, y_data, epochs=100, batch_size=32, callbacks=[WandbCallback(labels=y_data)])


class Over_Under_Model(Model):

    def run_over_under(self):  # Run
        pass


class Predict_ML_Model(Model):

    def run_predict_ml(self):  # Run
        pass


if __name__ == "__main__":
    x = Score_Model("NFL")
    self = x
    x.run_predict_score()
