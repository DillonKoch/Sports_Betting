# ==============================================================================
# File: nfl_spread.py
# Project: allison
# File Created: Sunday, 10th October 2021 7:57:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 10th October 2021 7:57:48 pm
# Modified By: Dillon Koch
# -----
#
# -----
# modeling NFL Spread bets
# ==============================================================================

import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential
from sklearn.linear_model import LogisticRegression
from tensorflow import keras
from wandb.keras import WandbCallback
from xgboost import XGBRegressor

import wandb

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_parent import Modeling_Parent

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)


class NFL_Spread(Modeling_Parent):
    def __init__(self):
        self.league = "NFL"
        self.confusion_matrix_title = "NFL Spread"

    def model_baseline_avg_points(self, avg_df_home_away_date, raw_df):  # Top Level
        """
        creating a baseline model that predicts a spread winner by predicting the final as
        each team's avg points scored in the last 10 games
        """
        # * left merge avg_df and the Home_Line_Close
        raw_df_home_line = raw_df[['Home', 'Away', 'Date', 'Home_Line_Close']]
        df = pd.merge(avg_df_home_away_date, raw_df_home_line, how='left', on=['Home', 'Away', 'Date'])

        # * make predictions, evaluate
        labels = df['Home_Covered']
        home_pts = df['Home_Final']
        away_pts = df['Away_Final']
        home_diff = home_pts - away_pts
        preds = home_diff > (-1 * df['Home_Line_Close'])

        self.plot_confusion_matrix(preds, labels, self.confusion_matrix_title)
        self.evaluation_metrics(preds, labels)
        self.spread_total_expected_return(preds, labels)

    def model_baseline_avg_point_differential(self, raw_df, avg_df_home_away_date):  # Top Level
        """
        creating a baseline model to predict spread winners based on each team's
        average point differential in the last 10 games
        """
        # TODO can do this once I add code for each team's points allowed, not just points scored!
        pass

    def model_xgboost(self, train_X, val_X, train_y, val_y):  # Top Level
        """
        modeling NFL spreads with XGBoost
        """
        print('-' * 50)
        print("XGBOOST")
        print('-' * 50)

        best_model = None
        best_total_winnings = -np.inf
        for n in range(25):
            print(n)
            model = XGBRegressor(n_estimators=n)
            model.fit(train_X, train_y)
            preds = model.predict(val_X)
            preds = np.array([item > 0.5 for item in preds])
            self.plot_confusion_matrix(preds, val_y, self.confusion_matrix_title)
            self.evaluation_metrics(preds, val_y)
            total_winnings = self.spread_total_expected_return(preds, val_y)
            if (best_model is None) or (total_winnings > best_total_winnings):
                best_model = model
                best_total_winnings = total_winnings

        print(f"BEST XGBOOST TOTAL WINNINGS: {best_total_winnings}")
        return best_model

    def model_logistic_regression(self, train_X, val_X, train_y, val_y):  # Top Level
        model = LogisticRegression(random_state=18, max_iter=10000)
        model.fit(train_X, train_y)
        preds = model.predict(val_X)
        self.plot_confusion_matrix(preds, val_y, self.confusion_matrix_title)
        self.evaluation_metrics(preds, val_y)
        self.spread_total_expected_return(preds, val_y)
        return model

    def model_neural_net(self, train_X, val_X, train_y, val_y):  # Top Level
        """
        modeling NFL spreads with a dense fully-connected neural net
        """
        n, m = train_X.shape
        model = Sequential()
        model.add(Dense(50, input_dim=m, kernel_initializer='normal', activation='relu'))
        model.add(Dense(30, kernel_initializer='normal', activation='relu'))
        model.add(Dense(1, kernel_initializer='normal'))
        opt = keras.optimizers.Adam(learning_rate=0.0001)
        model.compile(loss='mean_squared_error', optimizer=opt)
        model.summary()

        wandb.init(project='sports-betting', entity='dillonkoch')
        config = wandb.config
        config.learning_rate = 0.0001
        model.fit(train_X, train_y, validation_data=(val_X, val_y), epochs=130, callbacks=[WandbCallback()])

        preds = model.predict(val_X)
        preds = np.array([item[0] > 0.5 for item in preds])
        self.plot_confusion_matrix(preds, val_y, self.confusion_matrix_title)
        self.evaluation_metrics(preds, val_y)
        self.spread_total_expected_return(preds, val_y)

        return model

    def run(self):  # Run
        print("-" * 50)
        print("NFL SPREAD")
        print("-" * 50)

        # * loading data, baseline models
        raw_df = self.load_raw_df()
        avg_df = self.load_avg_df(['Home_Covered'], extra_cols=['Home_Line_Close'])
        avg_df_home_away_date = self.load_avg_df(['Home_Covered', 'Home', 'Away', 'Date'])

        # * balancing classes, splitting
        avg_df = self.balance_classes(avg_df, 'Home_Covered')
        train_X, val_X, train_y, val_y = self.split_avg_df(avg_df, ['Home_Covered'])
        train_y = train_y.values.ravel()
        val_y = val_y.values.ravel()

        # * Training Models
        # self.model_baseline_avg_points(avg_df_home_away_date, raw_df)
        # self.model_logistic_regression(train_X, val_X, train_y, val_y)
        # self.model_xgboost(train_X, val_X, train_y, val_y)
        self.model_neural_net(train_X, val_X, train_y, val_y)

        # * data prep, train test splitting
        # avg_df = self.balance_classes(avg_df, 'Home_Covered')
        # y = avg_df['Home_Covered']
        # X = avg_df[[col for col in list(avg_df.columns) if col != 'Home_Covered']]
        # X = self.scale_cols(X)
        # train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=18)  # TODO it's not splitting evenly across train/test

        # * non-baseline modeling
        # ! UNCOMMENT THE TYPE OF MODEL TO RUN
        # self.model_xgboost(train_X, val_X, train_y, val_y)
        # model = self.model_neural_net(train_X, val_X, train_y, val_y)
        # self.model_logistic_regression(train_X, val_X, train_y, val_y)

        # return avg_df


if __name__ == '__main__':
    x = NFL_Spread()
    self = x
    df = x.run()
