# ==============================================================================
# File: nfl_ml.py
# Project: allison
# File Created: Friday, 22nd October 2021 11:18:50 am
# Author: Dillon Koch
# -----
# Last Modified: Friday, 22nd October 2021 11:18:51 am
# Modified By: Dillon Koch
# -----
#
# -----
# modeling NFL MoneyLine bets
# ==============================================================================


import sys
from os.path import abspath, dirname

import numpy as np
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential
from sklearn.linear_model import LogisticRegression
from tensorflow import keras
from wandb.keras import WandbCallback

import wandb

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_parent import Modeling_Parent


class NFL_ML(Modeling_Parent):
    def __init__(self):
        self.league = "NFL"
        self.confusion_matrix_title = "NFL MoneyLine (1=Home Win)"

    def model_baseline_favored_team(self, raw_df):  # Top Level
        """
        baseline model for predicting ML's that just picks the favored team every time
        """
        raw_df = self.add_home_favored_col(raw_df)
        preds = raw_df['Home_Favored']
        labels = raw_df['Home_Win']
        home_mls = raw_df['Home_ML']
        away_mls = raw_df['Away_ML']
        self.plot_confusion_matrix(preds, labels, self.confusion_matrix_title)
        self.evaluation_metrics(preds, labels)
        self.moneyline_expected_return(preds, labels, home_mls, away_mls)

    def model_logistic_regression(self, train_X, val_X, train_y, val_y, val_y_home_mls, val_y_away_mls):  # Top Level
        model = LogisticRegression(random_state=18, max_iter=10000)
        model.fit(train_X, train_y)
        preds = model.predict(val_X)
        self.plot_confusion_matrix(preds, val_y, self.confusion_matrix_title)
        self.evaluation_metrics(preds, val_y)
        self.moneyline_expected_return(preds, val_y, val_y_home_mls, val_y_away_mls)
        return model

    def model_svm(self, train_X, val_X, train_y, val_y, val_y_home_mls, val_y_away_mls):  # Top Level
        pass

    def model_neural_net(self, train_X, val_X, train_y, val_y, val_y_home_mls, val_y_away_mls):  # Top Level
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
        model.fit(train_X, train_y, validation_data=(val_X, val_y), epochs=100, callbacks=[WandbCallback()])

        preds = model.predict(val_X)
        binary_preds = np.array([item[0] > 0.5 for item in preds])
        self.plot_confusion_matrix(binary_preds, val_y, self.confusion_matrix_title)
        self.evaluation_metrics(binary_preds, val_y)
        self.moneyline_expected_return(binary_preds, val_y, val_y_home_mls, val_y_away_mls)
        return model

    def run(self):  # Run
        print("-" * 50)
        print("NFL MONEYLINE")
        print("-" * 50)

        # * Loading data
        raw_df = self.load_raw_df()
        avg_df = self.load_avg_df(['Home_Win', 'Home_ML', 'Away_ML'])
        avg_df = self.balance_classes(avg_df, 'Home_Win')
        train_X, val_X, train_y, val_y = self.split_avg_df(avg_df, ['Home_Win', 'Home_ML', 'Away_ML'])
        val_y_home_mls = val_y['Home_ML']
        val_y_away_mls = val_y['Away_ML']
        train_y = train_y['Home_Win'].astype(int)
        val_y = val_y['Home_Win'].astype(int)

        # * Training models
        self.model_baseline_favored_team(raw_df)
        self.model_logistic_regression(train_X, val_X, train_y, val_y, val_y_home_mls, val_y_away_mls)
        self.model_neural_net(train_X, val_X, train_y, val_y, val_y_home_mls, val_y_away_mls)


if __name__ == '__main__':
    x = NFL_ML()
    self = x
    x.run()
