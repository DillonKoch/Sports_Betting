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

import pandas as pd
import tensorflow as tf
from keras.layers import Dense
from keras.models import Sequential
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import mean_absolute_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from xgboost import XGBRegressor
import wandb
from wandb.keras import WandbCallback


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_data import Modeling_Data

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)


class NFL_Spread:
    def __init__(self):
        pass

    def load_df(self):  # Top Level
        modeling_data = Modeling_Data("NFL")
        # df = modeling_data.run(['Home_Line_Close', 'Home_Covered'])
        df = modeling_data.run(['Home_Covered'])
        return df

    def balance_classes(self, df):  # Top Level
        pos_class = df[df['Home_Covered'] == 1]
        pos_class.reset_index(inplace=True, drop=True)
        neg_class = df[df['Home_Covered'] == 0]
        neg_class.reset_index(inplace=True, drop=True)
        lower_class = min([len(pos_class), len(neg_class)])
        balanced_df = pd.concat([pos_class.iloc[:lower_class], neg_class.iloc[:lower_class]])
        balanced_df.reset_index(inplace=True, drop=True)
        return balanced_df

    def scale_cols(self, X):  # Top Level
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        return X

    def model_xgboost(self, train_X, val_X, train_y, val_y):  # Top Level
        for n in range(100):
            print(n)
            model = XGBRegressor(n_estimators=n)
            model.fit(train_X, train_y)
            preds = model.predict(val_X)
            binary_preds = preds > 0.5
            self._compare_binary_preds(binary_preds, val_y)
            mae = mean_absolute_error(preds, val_y)
            # print(mae)

    def model_logistic_regression(self, train_X, val_X, train_y, val_y):  # Top Level
        clf = LogisticRegression(random_state=18, max_iter=1000)
        clf.fit(train_X, train_y)
        preds = clf.predict(val_X)
        binary_preds = preds > 0
        self._compare_binary_preds(binary_preds, val_y)
        mae = mean_absolute_error(preds, val_y)
        print(mae)
        return clf

    def model_neural_net(self, train_X, val_X, train_y, val_y):  # Top Level
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
        model.fit(train_X, train_y, validation_data=(val_X, val_y), epochs=30, callbacks=[WandbCallback()])

        preds = model.predict(val_X)
        binary_preds = preds > 0.5
        self._compare_binary_preds(binary_preds, val_y)
        return model

    def _compare_binary_preds(self, binary_preds, val_y):  # Global Helper
        correct = 0
        incorrect = 0
        for binary_pred, val in zip(binary_preds, val_y):
            if binary_pred == val:
                correct += 1
            else:
                incorrect += 1
        print(f"correct: {correct}, incorrect: {incorrect} ({round((100*(correct/(correct+incorrect))), 2)}% accuracy)")

    def run(self):  # Run
        df = self.load_df()
        df = self.balance_classes(df)
        y = df['Home_Covered']
        X = df[[col for col in list(df.columns) if col != 'Home_Covered']]
        X = self.scale_cols(X)
        # X = self.balance_X(X, y)
        train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=18)  # TODO it's not splitting evenly across train/test

        # ! UNCOMMENT THE TYPE OF MODEL TO RUN
        self.model_xgboost(train_X, val_X, train_y, val_y)
        # model = self.model_neural_net(train_X, val_X, train_y, val_y)
        # self.model_logistic_regression(train_X, val_X, train_y, val_y)

        return df


if __name__ == '__main__':
    x = NFL_Spread()
    self = x
    df = x.run()
