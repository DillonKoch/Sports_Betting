# ==============================================================================
# File: model.py
# Project: Modeling
# File Created: Monday, 6th July 2020 6:45:05 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 27th July 2020 5:27:04 pm
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

wandb.init(project="sports-betting")


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

    def home_win_pct_model(self, X_len):  # Top Level
        """
        model for predicting % chance home team wins
        """
        X_len = 209 if X_len is None else X_len
        model = keras.Sequential([
            keras.layers.Dense(256, input_shape=([X_len]), activation='relu'),
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
        adds binary col to indicate if home team won or not
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

    def train_home_win_pct(self):  # Run
        """
        trains model to predict the % change the home team wins / away team loses
        """
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
        X_len = X_data.shape[1]
        y_data = np.array(y_data).astype(int)

        model = self.home_win_pct_model(X_len)
        model.fit([X_data], y_data, epochs=30, batch_size=16, callbacks=[WandbCallback(data_type="data", labels=y_data)])
        self.save_model(model, "{}_Home_Win_pct.h5".format(self.league))
        return model

    def sb_moneyline_model(self, X_len):  # Top Level
        """
        model for predicting what the home/away moneyline will be for a game
        """
        X_len = 209 if X_len is None else X_len
        model = keras.Sequential([
            keras.layers.Dense(256, input_shape=([X_len]), activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(2, activation='linear')
        ])
        opt = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=opt,
                      loss="mse",
                      metrics=['accuracy'])
        return model

    def _clean_moneyline_df(self, moneyline_df):  # Specific Helper train_sb_moneyline

        def clean_ml_col(row, col_name):
            ml = float(row[col_name])
            ml = 100 if ml == "NL" else ml

            ml = row[col_name]

            if ((ml == 100) or (ml == -100)):
                return 0
            elif (ml > 100):
                return ml - 100
            else:
                return ml + 100

        moneyline_df['Home_ML'] = moneyline_df.apply(lambda row: clean_ml_col(row, "Home_ML"), axis=1)
        moneyline_df['Away_ML'] = moneyline_df.apply(lambda row: clean_ml_col(row, "Away_ML"), axis=1)
        return moneyline_df

    def train_sb_moneyline(self):  # Run
        ml_df, target_df = self.load_data()
        moneyline_cols = ["Home_ML", "Away_ML"]
        moneyline_df = target_df.loc[:, moneyline_cols]
        moneyline_df = self._clean_moneyline_df(moneyline_df)
        full_df = pd.concat([ml_df, moneyline_df], axis=1)
        full_df = full_df.dropna(axis=0)
        full_df = self.remove_non_ml_cols(full_df)

        X_cols = [col for col in list(full_df.columns) if col not in moneyline_cols]
        X_data = full_df.loc[:, X_cols]
        y_data = full_df.loc[:, moneyline_cols]

        X_data = np.array(X_data).astype(float)
        X_len = X_data.shape[1]
        y_data = np.array(y_data).astype(int)

        model = self.sb_moneyline_model(X_len)
        model.fit([X_data], y_data, epochs=120, batch_size=16, callbacks=[WandbCallback(data_type="data", labels=y_data)])
        self.save_model(model, "{}_SB_Moneyline.h5".format(self.league))
        return model

    def sb_spread_model(self, X_len):  # Top Level
        """
        Model for predicting the spread of a game
        """
        X_len = 209 if X_len is None else X_len
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

    def train_sb_spread(self):  # Run
        """
        training a model to predict the sportsbook's spread for a game
        """
        ml_df, target_df = self.load_data()
        spread_cols = ["Close_Home_Line", "Close_Away_Line"]
        spread_df = target_df.loc[:, spread_cols]
        full_df = pd.concat([ml_df, spread_df], axis=1)
        full_df = full_df.dropna(axis=0)
        full_df = self.remove_non_ml_cols(full_df)

        X_cols = [col for col in list(full_df.columns) if col not in spread_cols]
        X_data = full_df.loc[:, X_cols]
        y_data = full_df.loc[:, spread_cols]

        X_data = np.array(X_data).astype(float)
        y_data = np.array(y_data).astype(int)

        model = self.sb_spread_model()
        model.fit(X_data, y_data, epochs=85, batch_size=32, callbacks=[WandbCallback(labels=y_data)])
        self.save_model(model, "{}_SB_Spread.h5".format(self.league))

    def final_score_model(self, X_len):  # Top Level
        """
        model for predicting the final score of a game
        """
        X_len = 209 if X_len is None else X_len
        model = keras.Sequential([
            keras.layers.Dense(256, input_shape=([X_len]), activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(2, activation='linear')
        ])
        opt = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=opt,
                      loss="mse",
                      metrics=['accuracy'])
        return model

    def train_final_score(self):  # Run
        """
        trains a model to predict the final score of a game
        """
        ml_df, target_df = self.load_data()
        score_cols = ["Home_Score_x", "Away_Score_x"]
        score_df = target_df.loc[:, score_cols]
        full_df = pd.concat([ml_df, score_df], axis=1)
        full_df = full_df.dropna(axis=0)
        full_df = self.remove_non_ml_cols(full_df)

        X_cols = [col for col in list(full_df.columns) if col not in score_cols]
        X_data = full_df.loc[:, X_cols]
        X_len = X_data.shape[1]
        y_data = full_df.loc[:, score_cols]

        X_data = np.array(X_data).astype(float)
        y_data = np.array(y_data).astype(int)

        model = self.final_score_model(X_len)
        model.fit(X_data, y_data, epochs=70, batch_size=32, callbacks=[WandbCallback(labels=y_data)])
        self.save_model(model, "{}_Final_Score.h5".format(self.league))

    def get_home_spread_won_col(self, target_df):  # Top Level
        """
        adds column to target_df indicating if the home team covered the spread
        """
        target_df['Home_Spread_Won'] = None

        def home_spread_won(row):
            home_score = row['Home_Score_x']
            away_score = row['Away_Score_x']
            home_spread = row['Close_Home_Line']
            home_spread = home_spread.replace('--', '-').replace("+-", "-")
            home_spread = float(home_spread) if home_spread.lower() != "nl" else 0.0
            home_spread_score = home_score + home_spread
            if home_spread_score == away_score:  # push
                home_spread_won = 0.5
            elif home_spread_score > away_score:  # home team covers
                home_spread_won = 1
            else:
                home_spread_won = 0  # away team covers
            return home_spread_won

        target_df['Home_Spread_Won'] = target_df.apply(lambda row: home_spread_won(row), axis=1)
        return target_df

    def home_spread_win_pct_model(self, X_len=None):  # Top Level
        """
        model for predicting the % chance the home team covers the spread
        """
        X_len = 209 if X_len is None else X_len
        model = keras.Sequential([
            keras.layers.Dense(256, input_shape=([X_len]), activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        opt = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=opt,
                      loss="mse",
                      metrics=['accuracy'])
        return model

    def train_home_spread_win_pct(self):  # Run
        ml_df, target_df = self.load_data()
        target_df = self.get_home_spread_won_col(target_df)
        home_spread_win_df = target_df['Home_Spread_Won']
        full_df = pd.concat([ml_df, home_spread_win_df], axis=1)
        full_df = full_df.dropna(axis=0)
        full_df = self.remove_non_ml_cols(full_df)

        X_cols = [c for c in list(full_df.columns) if c != "Home_Spread_Won"]
        X_data = full_df.loc[:, X_cols]
        y_data = full_df.loc[:, ["Home_Spread_Won"]]

        X_data = np.array(X_data).astype(float)
        X_len = X_data.shape[1]
        y_data = np.array(y_data).astype(float)

        model = self.home_spread_win_pct_model(X_len)
        model.fit(X_data, y_data, epochs=95, batch_size=32, callbacks=[WandbCallback(labels=y_data)])
        self.save_model(model, "{}_Home_Spread_Win_pct.h5".format(self.league))

    def sb_over_under_model(self, X_data):  # Top Level
        """
        model to predict what the over under from the sportsbook will be
        """
        X_len = len(X_data)
        model = keras.Sequential([
            keras.layers.Dense(256, input_shape=([X_len]), activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(1, activation='linear')
        ])
        opt = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=opt, loss='mse')
        return model

    def train_sb_over_under(self):  # Run
        """
        trains a model to predict what the over under given from the sportsbook will be
        """
        ml_df, target_df = self.load_data()
        ou_df = target_df.loc[:, ["Close_OU"]]
        full_df = pd.concat([ml_df, ou_df], axis=1)
        full_df = full_df.dropna(axis=0)
        full_df = self.remove_non_ml_cols(full_df)

        X_cols = [c for c in list(full_df.columns) if c != "Close_OU"]
        X_data = full_df.loc[:, X_cols]
        y_data = full_df.loc[:, ["Close_OU"]]

        X_data = np.array(X_data).astype(float)
        y_data = np.array(y_data).astype(float)

        model = self.sb_over_under_model()
        model.fit(X_data, y_data, epochs=70, batch_size=32, callbacks=[WandbCallback(labels=y_data)])
        self.save_model(model, "{}_SB_Over_Under.h5".format(self.league))

    def get_total_points_col(self, target_df):  # Top Level
        target_df['Point_Total'] = target_df['Home_Score_x'] + target_df['Away_Score_x']
        return target_df

    def predict_point_total_model(self):  # Top Level
        """
        model to predict the total amount of points in a game
        """
        model = keras.Sequential([
            keras.layers.Dense(256, input_shape=([209]), activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(1, activation='linear')
        ])
        opt = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=opt, loss='mse')
        return model

    def train_point_total(self):  # Run
        """
        trains a model to predict the point total for a game
        """
        ml_df, target_df = self.load_data()
        target_df = self.get_total_points_col(target_df)
        point_total_df = target_df['Point_Total']

        full_df = pd.concat([ml_df, point_total_df], axis=1)
        full_df = full_df.dropna(axis=0)
        full_df = self.remove_non_ml_cols(full_df)

        X_cols = [c for c in list(full_df.columns) if c != "Point_Total"]
        X_data = full_df.loc[:, X_cols]
        y_data = full_df.loc[:, ["Point_Total"]]

        X_data = np.array(X_data).astype(float)
        y_data = np.array(y_data).astype(float)

        model = self.predict_point_total_model()
        model.fit(X_data, y_data, epochs=110, batch_size=32, callbacks=[WandbCallback(labels=y_data)])
        self.save_model(model, "{}_Point_Total.h5".format(self.league))

    def get_over_won_col(self, target_df):  # Top Level
        """
        adds binary col to indicate if the over won or not
        """
        target_df = self.get_total_points_col(target_df)
        target_df['Over_Won'] = None

        def over_won(row):
            return 1 if row['Point_Total'] > row['Close_OU'] else 0

        target_df['Over_Won'] = target_df.apply(lambda row: over_won(row), axis=1)
        return target_df

    def bet_over_under_model(self):  # Top Level
        """
        model to predict the % chance the over will win
        """
        model = keras.Sequential([
            keras.layers.Dense(256, input_shape=([209]), activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(1, activation='sigmoid')
        ])
        opt = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=opt, loss='mse')
        return model

    def train_over_win_pct(self):  # Run
        ml_df, target_df = self.load_data()
        target_df = self.get_over_won_col(target_df)
        over_won_df = target_df['Over_Won']

        full_df = pd.concat([ml_df, over_won_df], axis=1)
        full_df = full_df.dropna(axis=0)
        full_df = self.remove_non_ml_cols(full_df)

        X_cols = [c for c in list(full_df.columns) if c != "Over_Won"]
        X_data = full_df.loc[:, X_cols]
        y_data = full_df.loc[:, ["Over_Won"]]

        X_data = np.array(X_data).astype(float)
        y_data = np.array(y_data).astype(float)

        model = self.bet_over_under_model()
        model.fit(X_data, y_data, epochs=70, batch_size=32, callbacks=[WandbCallback(labels=y_data)])
        self.save_model(model, "{}_Over_Win_pct.h5".format(self.league))


if __name__ == "__main__":
    x = Model("NBA")
    self = x
    ml_df, target_df = x.load_data()
    x.train_sb_moneyline()
