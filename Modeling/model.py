# ==============================================================================
# File: model.py
# Project: Modeling
# File Created: Monday, 6th July 2020 6:45:05 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 18th July 2020 5:26:30 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for building models to predict one of the target variables in the PROD data
# ==============================================================================


import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras

import wandb
from wandb.keras import WandbCallback

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)

# wandb.init(project="sports-betting")


class Model:
    """
    class for creating models to predict one of the target variables in the PROD df
    """

    def __init__(self, league: str):
        self.league = league

    def load_data(self, training=True):  # Top Level
        """
        loads the ml_df and target_df created from prod_to_ml.py
        """
        try:
            ml_path = ROOT_PATH + "/Modeling/{}_ml.csv".format(self.league.lower())
            ml_df = pd.read_csv(ml_path)
            target_path = ROOT_PATH + "/Modeling/{}_target.csv".format(self.league.lower())
            target_df = pd.read_csv(target_path)
        except FileNotFoundError:
            print("Could not find ml and target df for {} - run the prod_to_ml.py script!".format(self.league))
            return None

        if training:
            ml_df = ml_df.loc[ml_df.Final_Status.notnull()]
            target_df = target_df.loc[target_df.Final_Status.notnull()]

        return ml_df, target_df

    def remove_non_ml_cols(self, df):  # Top Level
        """
        takes out ESPN_ID, datetime, final status from a df
        """
        non_ml_cols = ["ESPN_ID", "datetime", "Final_Status"]
        cols = [col for col in list(df.columns) if col not in non_ml_cols]
        return df.loc[:, cols]

    def oversample_even_classes(self, df, target_col):  # Top Level
        """
        oversamples the df to make the target_col a 50/50 split
        """
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
        """
        saves a model to the appropriate location
        """
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
            keras.layers.Dense(256, input_shape=([209]), activation='relu'),
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

    def train_home_win_model(self):  # Run
        ml_df, target_df = self.load_data()
        home_win_col = self.get_home_win_col(target_df)
        full_df = pd.concat([ml_df, home_win_col], axis=1)
        full_df = full_df.dropna(axis=0)
        full_df = self.oversample_even_classes(full_df, "Home_win")
        full_df = self.remove_non_ml_cols(full_df)

        X_cols = [col for col in list(full_df.columns) if col != "Home_win"]
        X_data = full_df.loc[:, X_cols]
        y_data = full_df.loc[:, 'Home_win']

        X_data = np.array(X_data).astype(float)
        y_data = np.array(y_data).astype(int)

        model = self.home_win_model()
        model.fit([X_data], y_data, epochs=30, batch_size=16, callbacks=[WandbCallback(data_type="data", labels=y_data)])
        self.save_model(model, "{}_Home_Win.h5".format(self.league))
        return model

    def predict_score_model(self):  # Top Level
        model = keras.Sequential([
            keras.layers.Dense(256, input_shape=([209]), activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(2, activation='linear')
        ])
        opt = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=opt,
                      loss="mse",
                      metrics=['accuracy'])
        return model

    def train_predict_score(self):
        ml_df, target_df = self.load_data()
        score_cols = ["Home_Score_x", "Away_Score_x"]
        score_df = target_df.loc[:, score_cols]
        full_df = pd.concat([ml_df, score_df], axis=1)
        full_df = full_df.dropna(axis=0)
        full_df = self.remove_non_ml_cols(full_df)

        X_cols = [col for col in list(full_df.columns) if col not in score_cols]
        X_data = full_df.loc[:, X_cols]
        y_data = full_df.loc[:, score_cols]

        X_data = np.array(X_data).astype(float)
        y_data = np.array(y_data).astype(int)

        model = self.predict_score_model()
        model.fit(X_data, y_data, epochs=70, batch_size=32, callbacks=[WandbCallback(labels=y_data)])
        self.save_model(model, "{}_Predict_Score.h5".format(self.league))


class Over_Under_Model(Model):

    def sb_over_under_model(self):  # Top Level
        """
        model to predict what the over under from the sportsbook will be
        """
        pass

    def train_sb_over_under(self):  # Run
        """
        trains a model to predict what the over under given from the sportsbook will be
        """
        ml_df, target_df = self.load_data()
        ou_df = target_df.loc[:, ["Close_OU"]]
        full_df = pd.concat([ml_df, ou_df], axis=1)
        full_df = full_df.dropna(axis=0)
        full_df = self.remove_non_ml_cols(full_df)

        X_cols = list(full_df.columns).remove("Close_OU")
        X_data = full_df.loc[:, X_cols]
        y_data = full_df.loc[:, ["Close_OU"]]

        X_data = np.array(X_data).astype(float)
        y_data = np.array(y_data).astype(float)

        model = self.over_under_model()
        model.fit(X_data, y_data, epochs=70, batch_size=32, callbacks=[WandbCallback(labels=y_data)])
        self.save_model(model, "{}_Over_Under.h5".format(self.league))


class Predict_ML_Model(Model):

    def train_predict_ml(self):  # Run
        pass


if __name__ == "__main__":
    x = Score_Model("NFL")
    self = x
    ml_df, target_df = x.load_data()
    # x.train_predict_score()
