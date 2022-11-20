# ==============================================================================
# File: NFL_ML.py
# Project: Modeling
# File Created: Saturday, 12th September 2020 8:09:08 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 14th September 2020 10:04:27 am
# Modified By: Dillon Koch
# -----
#
# -----
# Building models to predict NFL Moneylines
# ==============================================================================


import sys
from os.path import abspath, dirname

import wandb
from wandb.keras import WandbCallback
import pandas as pd
import numpy as np
from tensorflow import keras
from sklearn.model_selection import train_test_split


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.model_parent import Model_Parent


class NFL_ML(Model_Parent):
    def __init__(self):
        super().__init__("NFL")
        wandb.init()

    def get_X_data(self, df):
        X_cols = list(df.columns)
        X_cols = X_cols[X_cols.index('home_ovr_wins'):X_cols.index('Line')]
        X_df = df.loc[:, X_cols]
        X_df.fillna(0, inplace=True)
        return X_df

    def get_ml_cols(self, df):
        odds_home_ml = list(df['Home_ML'])
        odds_home_ml = [val + 100 if val < 0 else val - 100 for val in odds_home_ml]

        odds_away_ml = df['Away_ML']
        odds_away_ml = [val + 100 if val < 0 else val - 100 for val in odds_away_ml]

        return odds_home_ml, odds_away_ml

    def predict_ml_model(self):
        model = keras.Sequential([
            keras.layers.Dense(256, input_shape=([177]), activation='relu'),
            keras.layers.Dense(184, activation='relu'),
            keras.layers.Dense(128, activation='relu'),
            keras.layers.Dense(64, activation='relu'),
            keras.layers.Dense(32, activation='relu'),
            keras.layers.Dense(2, activation='linear'),
        ])
        opt = keras.optimizers.Adam(learning_rate=0.001)
        model.compile(optimizer=opt, loss='mse')
        return model

    def train_predict_ml(self):  # Run
        df = self.load_data()
        df = df.loc[df.Home_ML.notnull() & df.Away_ML.notnull()]
        df = df.loc[df.home_first_downs.notnull()]
        X_df = self.get_X_data(df)
        odds_home_ml, odds_away_ml = self.get_ml_cols(df)
        model = self.predict_ml_model()

        X_df = np.array(X_df).astype(float)
        y = pd.DataFrame({'home': odds_home_ml, 'away': odds_away_ml})
        y = np.array(y).astype(float)

        X_train, X_test, y_train, y_test = train_test_split(X_df, y, train_size=0.8)

        model.fit(X_train, y_train, epochs=100, batch_size=16, validation_data=(X_test, y_test),
                  callbacks=[WandbCallback()])

        return model


if __name__ == '__main__':
    x = NFL_ML()
    self = x
    model = x.train_predict_ml()
