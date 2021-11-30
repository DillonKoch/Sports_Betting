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
from keras.layers import Dense
from keras.models import Sequential
from sklearn.linear_model import LogisticRegression
from tensorflow import keras
from wandb.keras import WandbCallback

import wandb

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_parent import ML_Parent


class NFL_ML(ML_Parent):
    def __init__(self):
        super().__init__()
        self.league = "NFL"

    def model_baseline(self):  # Top Level
        pass

    # def model_baseline_favored_team(self, raw_df):  # Top Level
    #     """
    #     baseline model for predicting ML's that just picks the favored team every time
    #     """
    #     raw_df = self.add_home_favored_col(raw_df)
    #     preds = raw_df['Home_Favored']
    #     labels = raw_df['Home_Win']
    #     home_mls = raw_df['Home_ML']
    #     away_mls = raw_df['Away_ML']
    #     self.plot_confusion_matrix(preds, labels, self.confusion_matrix_title)
    #     self.evaluation_metrics(preds, labels)
    #     self.moneyline_expected_return(preds, labels, home_mls, away_mls)

    # def model_neural_net(self, train_X, val_X, train_y, val_y, val_y_home_mls, val_y_away_mls):  # Top Level
    #     n, m = train_X.shape
    #     model = Sequential()
    #     model.add(Dense(50, input_dim=m, kernel_initializer='normal', activation='relu'))
    #     model.add(Dense(30, kernel_initializer='normal', activation='relu'))
    #     model.add(Dense(1, kernel_initializer='normal'))
    #     opt = keras.optimizers.Adam(learning_rate=0.0001)
    #     model.compile(loss='mean_squared_error', optimizer=opt)
    #     model.summary()

    #     wandb.init(project='sports-betting', entity='dillonkoch')
    #     config = wandb.config
    #     config.learning_rate = 0.0001
    #     model.fit(train_X, train_y, validation_data=(val_X, val_y), epochs=100, callbacks=[WandbCallback()])

    #     preds = model.predict(val_X)
    #     binary_preds = np.array([item[0] > 0.5 for item in preds])
    #     self.plot_confusion_matrix(binary_preds, val_y, self.confusion_matrix_title)
    #     self.evaluation_metrics(binary_preds, val_y)
    #     self.moneyline_expected_return(binary_preds, val_y, val_y_home_mls, val_y_away_mls)
    #     return model


if __name__ == '__main__':
    x = NFL_ML()
    self = x
    x.run()
