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

import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential
from tensorflow import keras
from wandb.keras import WandbCallback

import wandb

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_parent import Spread_Parent

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)


class NFL_Spread(Spread_Parent):
    def __init__(self):
        super().__init__()
        self.league = "NFL"

    def model_baseline(self):  # Top Level
        pass

    def model_neural_net(self, train_X, val_X, train_y, val_y):  # Top Level
        pass

    # def model_baseline_avg_points(self, avg_df_home_away_date, raw_df):  # Top Level
    #     """
    #     creating a baseline model that predicts a spread winner by predicting the final as
    #     each team's avg points scored in the last 10 games
    #     """
    #     # * left merge avg_df and the Home_Line_Close
    #     raw_df_home_line = raw_df[['Home', 'Away', 'Date', 'Home_Line_Close']]
    #     df = pd.merge(avg_df_home_away_date, raw_df_home_line, how='left', on=['Home', 'Away', 'Date'])

    #     # * make predictions, evaluate
    #     labels = df['Home_Covered']
    #     home_pts = df['Home_Final']
    #     away_pts = df['Away_Final']
    #     home_diff = home_pts - away_pts
    #     preds = home_diff > (-1 * df['Home_Line_Close'])

    #     self.plot_confusion_matrix(preds, labels, self.confusion_matrix_title)
    #     self.evaluation_metrics(preds, labels)
    #     self.spread_total_expected_return(preds, labels)

    # def model_baseline_avg_point_differential(self, raw_df, avg_df_home_away_date):  # Top Level
    #     """
    #     creating a baseline model to predict spread winners based on each team's
    #     average point differential in the last 10 games
    #     """
    #     # TODO can do this once I add code for each team's points allowed, not just points scored!
    #     pass

    # def model_neural_net(self, train_X, val_X, train_y, val_y):  # Top Level
    #     """
    #     modeling NFL spreads with a dense fully-connected neural net
    #     """
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
    #     model.fit(train_X, train_y, validation_data=(val_X, val_y), epochs=130, callbacks=[WandbCallback()])

    #     preds = model.predict(val_X)
    #     preds = np.array([item[0] > 0.5 for item in preds])
    #     self.plot_confusion_matrix(preds, val_y, self.confusion_matrix_title)
    #     self.evaluation_metrics(preds, val_y)
    #     self.spread_total_expected_return(preds, val_y)

    #     return model


if __name__ == '__main__':
    x = NFL_Spread()
    self = x
    x.run_all()
