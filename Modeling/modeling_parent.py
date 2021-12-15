# ==============================================================================
# File: modeling_parent.py
# Project: allison
# File Created: Friday, 19th November 2021 11:05:46 am
# Author: Dillon Koch
# -----
# Last Modified: Friday, 19th November 2021 11:05:47 am
# Modified By: Dillon Koch
# -----
#
# -----
# Shared code between all modeling files belongs in this parent class
# ==============================================================================


import copy
import datetime
import os
import random
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
import tensorflow as tf
from keras.callbacks import EarlyStopping
from keras.layers import Dense
from keras.models import Sequential
from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
from tensorflow import keras
from wandb.keras import WandbCallback

import wandb

physical_devices = tf.config.experimental.list_physical_devices('GPU')
if len(physical_devices) > 0:
    tf.config.experimental.set_memory_growth(physical_devices[0], True)


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Modeling_Parent:
    def __init__(self):
        self.model_method_dict = {"logistic regression": self.model_logistic_regression,
                                  "random forest": self.model_random_forest,
                                  "svm": self.model_svm,
                                  "neural net": self.model_neural_net}

    @property
    def temp_model_checkpoint_path(self):  # Property
        return ROOT_PATH + f"/Models/{self.league}/temp_{self.bet_type}_model.h5"

    @property
    def best_model_checkpoint_path(self):  # Property
        return ROOT_PATH + f"/Models/{self.league}/best_{self.bet_type}_model.h5"

    def model_logistic_regression(self, train_X, val_X, train_y, val_y):  # Top Level
        model = LogisticRegression(random_state=18, max_iter=10000)
        model.fit(train_X, train_y)
        # preds = model.predict_proba(val_X)
        return model

    def model_random_forest(self, train_X, val_X, train_y, val_y):  # Top Level
        model = RandomForestClassifier(max_depth=10, random_state=18, n_estimators=100)
        model.fit(train_X, train_y)
        # preds = model.predict_proba(val_X)
        return model

    def model_svm(self, train_X, val_X, train_y, val_y):  # Top Level
        model = svm.SVC(probability=True, kernel='linear')
        model.fit(train_X, train_y)
        # preds = model.predict_proba(val_X)
        return model

    def _wandb_setup(self):  # Specific Helper model_neural_net
        wandb.init(project='sports-betting', entity='dillonkoch')
        config = wandb.config
        config.learning_rate = 0.0001

    def _neural_net_callback(self):  # Specific Helper model_neural_net
        """
        callback for saving the model after the best val_loss
        """
        model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
            filepath=self.temp_model_checkpoint_path,
            save_weights_only=False,
            monitor='val_loss',
            save_best_only=True
        )
        return model_checkpoint_callback

    def _neural_net_model(self, train_X, layers):  # Specific Helper model_neural_net
        """
        building neural net models with a given layer architecture
        """
        n, m = train_X.shape
        model = Sequential()
        model.add(Dense(layers[0], input_dim=m, kernel_initializer='normal', activation='relu'))
        for layer in layers[1:]:
            model.add(Dense(layer, kernel_initializer='normal', activation='relu'))
        model.add(Dense(1, kernel_initializer='normal', activation='sigmoid'))
        opt = keras.optimizers.Adam(learning_rate=0.0001)
        model.compile(loss='mean_squared_error', optimizer=opt)
        model.summary()
        return model

    def model_neural_net(self, train_X, val_X, train_y, val_y):  # Top Level
        """
        modeling NFL spreads with a dense fully-connected neural net
        """
        self._wandb_setup()
        model_checkpoint_callback = self._neural_net_callback()
        early_stopping_callback = EarlyStopping(monitor='val_loss', patience=3)
        layer_structures = [[50, 30], [100, 50], [200, 100], [200, 100, 50, 25],
                            [1000, 800, 600, 400, 200, 100], [750, 500, 250, 100, 50, 25]]
        lowest_val_loss = np.Inf
        for layer_struct in layer_structures:
            model = self._neural_net_model(train_X, layer_struct)
            history = model.fit(train_X, train_y, validation_data=(val_X, val_y), epochs=50,
                                callbacks=[early_stopping_callback, WandbCallback(), model_checkpoint_callback])
            val_loss = min(history.history['val_loss'])
            print(layer_struct, val_loss, lowest_val_loss)
            if val_loss < lowest_val_loss:
                model.save(self.best_model_checkpoint_path)
                lowest_val_loss = val_loss

        model = keras.models.load_model(self.best_model_checkpoint_path)
        return model, round(lowest_val_loss, 3)

    def _clean_mls(self, df):  # Specific Helper  load_df
        """
        Cleaning the ML cols to get rid of the huge gap from -100 to 100
        - so -110 goes to -10, +230 becomes 130, etc
        """
        ml_cols = [col for col in df.columns if "ML" == col[-2:]]
        for col in ml_cols:
            df[col] = df[col].apply(lambda x: x + 100 if x < 0 else x - 100)
        return df

    def load_df(self, past_games, player_stats):  # Top Level
        """
        loads a df from /Data/Modeling_Data with a certain # past games, and optional player stats
        - the dataframe has to be created with /Modeling/modeling_data.py first
        """
        player_stat_str = "player_stats" if player_stats else "no_player_stats"
        path = ROOT_PATH + f"/Data/Modeling_Data/{self.league}/{player_stat_str}_avg_{past_games}_past_games.csv"
        df = pd.read_csv(path)
        df = self._clean_mls(df)
        cols = [col for col in list(df.columns) if col not in self.remove_cols]
        df = df[cols]
        return df

    def split_finished_upcoming_games(self, df):  # Top Level
        """
        input to this function is the output from load_df()
        - splits the df into all games that are played (with target labels)
          and games that are not yet played, but have odds data available
        """
        betting_cols = ['Home_Line_Close', 'Home_Line_Close_ML', 'OU_Close', 'OU_Close_ML', 'Home_ML', 'Away_ML']
        finished_subset = [col for col in ['Home_Covered', 'Home_Win', 'Over_Covered'] if col in list(df.columns)]

        # finished has targets not null
        df_copy1 = copy.deepcopy(df)
        finished_games_df = df_copy1.dropna(subset=finished_subset + betting_cols)

        # unfinished has no targets, but betting odds
        df_copy2 = copy.deepcopy(df)
        targets_null_df = df_copy2.loc[~df_copy2.index.isin(df_copy2.dropna(subset=finished_subset).index)]
        upcoming_games_df = targets_null_df.dropna(subset=betting_cols)
        return finished_games_df, upcoming_games_df

    def _recent_20pct_test(self, df):  # Specific Helper split_train_test_df
        """
        returns a df with the last 20% of the data as test data
        """
        test_size = 0.2
        test_cutoff = int(len(df) - (len(df) * test_size))
        train_df = df.iloc[:test_cutoff, :]
        test_df = df.iloc[test_cutoff:, :]
        return train_df, test_df

    def _basic_20pct_split(self, df):  # Specific Helper split_train_test_
        """
        splits the data with a classic train_test_split call
        """
        indices = list(range(len(df)))
        random.shuffle(indices)
        indices_split_point = int(len(df) * 0.8)
        train_indices = indices[:indices_split_point]
        test_indices = indices[indices_split_point:]
        train_df = df.iloc[train_indices, :]
        test_df = df.iloc[test_indices, :]
        return train_df, test_df

    def split_train_test_df(self, df, dataset_split):  # Top Level
        if dataset_split == 'recent_20pct_test':
            train_df, test_df = self._recent_20pct_test(df)
        elif dataset_split == 'basic_20pct_split':
            train_df, test_df = self._basic_20pct_split(df)
        # ! add more options for train/test split here if desired
        return train_df, test_df

    def balance_classes(self, df):  # Top Level
        """
        balances the df so the self.target_col has equal amounts of each class
        - does this by oversampling until classes are equal -> not throwing away data
        """
        # * separating the dataset into those with positive/negative labels
        positive_data = df[df[self.target_col] == 1]
        positive_data.reset_index(inplace=True, drop=True)
        negative_data = df[df[self.target_col] == 0]
        negative_data.reset_index(inplace=True, drop=True)

        # * determining which is undersampled, and resampling latest games to make it even
        if len(positive_data) > len(negative_data):
            diff = len(positive_data) - len(negative_data)
            negative_data = pd.concat([negative_data, negative_data.iloc[-diff:, :]])
        else:
            diff = len(negative_data) - len(positive_data)
            positive_data = pd.concat([positive_data, positive_data.iloc[-diff:, :]])

        # * adding the two halves of the dataset back together
        balanced_df = pd.concat([positive_data, negative_data])
        return balanced_df

    def scaled_X_y(self, df, scaler=None):  # Top Level
        """
        """
        y = np.array(df[self.target_col])
        X_cols = [col for col in list(df.columns) if col not in ['Home', "Away", "Date", self.target_col]]
        X = np.array(df[X_cols])
        scaler = StandardScaler() if scaler is None else scaler
        X = scaler.fit_transform(X)
        return X, y, scaler

    def _make_load_df(self, test_set):  # Specific Helper make_preds
        """
        loads the predictions file for the league if it exists, otherwise makes it
        """
        test_str = "Test" if test_set else "Prod"
        path = ROOT_PATH + f"/Data/Predictions/{self.league}/{test_str}_Predictions.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
        else:
            df = pd.DataFrame(columns=["Game_Date", "Home", "Away", "Bet_Type", "Bet_Value",
                                       "Bet_ML", "Prediction", "Outcome", "Algorithm",
                                       "Avg_Past_Games", "Player_Stats", "Dataset", "Loss", "Pred_ts"])
        return df

    def _current_ts(self):  # Specific Helper  make_preds
        """returning a string of the current time"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def _ml_back_to_normal(self, ml):  # Specific Helper make_preds
        """
        converting the ML values back to usual for the predictions_df
        """
        return ml + 100 if ml > 0 else ml - 100

    def _save_preds(self, df, test_set):  # Specific Helper make_preds
        """
        sorting, dropping duplicates, and saving the predictions
        - saves to Test_Predictions or Prod_Predictions (prod is for games that are not played yet - real predictions!)
        """
        df.sort_values(by=["Game_Date", "Home", "Away", "Bet_Type", "Loss", "Algorithm", "Dataset"], inplace=True)
        df.drop_duplicates(subset=['Game_Date', 'Home', 'Away', 'Bet_Type', 'Bet_Value', 'Bet_ML',
                                   'Algorithm', 'Avg_Past_Games', 'Player_Stats', 'Dataset'], keep='last', inplace=True)
        test_str = "Test" if test_set else "Prod"
        df.to_csv(ROOT_PATH + f"/Data/Predictions/{self.league}/{test_str}_Predictions.csv", index=False)
        print(f"{test_str} Predictions saved!")

    def make_preds(self, model, upcoming_games_df, upcoming_games_X, alg, avg_past_games, player_stats_bool, test_set, dataset_split, lowest_val_loss):  # Top Level
        """
        making predictions on upcoming games and saving to /Data/Predictions/
        """
        df = self._make_load_df(test_set)
        preds = model.predict_proba(upcoming_games_X) if alg != 'neural net' else model.predict(upcoming_games_X)
        for i in range(len(upcoming_games_df)):
            game_row = upcoming_games_df.iloc[i, :]
            prediction = round(preds[i][1], 3) if alg != 'neural net' else round(preds[i][0], 3)
            bet_val = game_row[self.bet_value_col] if self.bet_type != "Moneyline" else None
            new_row = [game_row['Date'], game_row['Home'], game_row['Away'], self.bet_type,
                       bet_val, self._ml_back_to_normal(game_row[self.bet_ml_col]),
                       prediction, None, alg, avg_past_games, player_stats_bool, dataset_split, lowest_val_loss, self._current_ts()]
            df.loc[len(df)] = new_row
        self._save_preds(df, test_set)

    def run(self, df, dataset_split, alg, num_past_games, player_stat_bool):
        finished_games_df, upcoming_games_df = self.split_finished_upcoming_games(df)
        train_df, test_df = self.split_train_test_df(finished_games_df, dataset_split)
        balanced_train_df = self.balance_classes(train_df)

        train_X, train_y, scaler = self.scaled_X_y(balanced_train_df)
        test_X, test_y, _ = self.scaled_X_y(test_df, scaler)

        model_method = self.model_method_dict[alg]
        model, lowest_val_loss = model_method(train_X, test_X, train_y, test_y)

        if len(upcoming_games_df) > 0:
            upcoming_games_X, _, _ = self.scaled_X_y(upcoming_games_df, scaler=scaler)
            self.make_preds(model, upcoming_games_df, upcoming_games_X, alg, num_past_games, player_stat_bool, False, dataset_split, lowest_val_loss)
        # self.make_preds(model, test_df, test_X, alg, num_past_games, player_stat_bool, True, dataset_split)

    def run_all(self):  # Run
        """
        running all algorithms on all datasets
        """
        # dataset_splits = ['basic_20pct_split', 'recent_20pct_test']
        dataset_splits = ['basic_20pct_split']
        # algs = ['logistic regression', 'random forest', 'neural net']
        algs = ['neural net']
        num_past_games = [3, 5, 10, 15, 20, 25]
        player_stats_bools = [False, True]
        for dataset_split in dataset_splits:
            for alg in algs:
                for npg in num_past_games:
                    for player_stat_bool in player_stats_bools:

                        # * skipping some combinations
                        if (alg in ['svm']) and player_stat_bool:
                            continue

                        ps_str = "with" if player_stat_bool else "without"
                        print(f"{self.league} {self.bet_type} {alg} on past {npg} games {ps_str} player stats")
                        df = self.load_df(past_games=npg, player_stats=player_stat_bool)
                        self.run(df, dataset_split, alg, npg, player_stat_bool)


class Spread_Parent(Modeling_Parent):
    """
    Parent class for modeling spread betting
    """

    def __init__(self):
        super().__init__()
        self.bet_type = "Spread"
        self.bet_value_col = "Home_Line_Close"
        self.bet_ml_col = "Home_Line_Close_ML"
        self.target_col = "Home_Covered"
        self.remove_cols = ["Home_Win", "Over_Covered"]

    # def _expected_return_thresh(self, preds, labels, thresh):  # Specific Helper expected_return
    #     """
    #     computing the expected return when only placing on bets that the model
    #       is at least 'thresh' % confident on
    #     - thresh is the decimal pct for model confidence (0.6 -> model has to be >=60% confident)
    #     """
    #     assert (thresh >= 0.5) and (thresh <= 1.0), "thresh must be between 0.5 and 1.0"
    #     home_cover_preds = [item[1] for item in preds]
    #     thresh_preds = []
    #     thresh_labels = []
    #     for pred, label in zip(home_cover_preds, list(labels)):
    #         if abs(pred - 0.5) > (thresh - 0.5):
    #             thresh_preds.append(pred)
    #             thresh_labels.append(label)

    #     return np.array(thresh_preds), np.array(thresh_labels)

    # def expected_return(self, preds, labels, thresh=0.5):  # Top Level
    #     preds, labels = self._expected_return_thresh(preds, labels, thresh)
    #     binary_preds = np.array([1 if pred >= 0.5 else 0 for pred in preds])
    #     num_bets = len(binary_preds)
    #     correct = (binary_preds == labels).sum()
    #     incorrect = num_bets - correct
    #     pct_accuracy = round(correct / (correct + incorrect), 2)
    #     total_winnings = (correct * (10 / 11)) - incorrect
    #     expected_return_on_dollar = round(total_winnings / num_bets, 4)
    #     print(f"Won/Lost ${round(total_winnings,2)} on {num_bets} bets at {thresh} threshold, for {round(expected_return_on_dollar, 2)} expected return per dollar")
    #     return pct_accuracy, expected_return_on_dollar


class Total_Parent(Spread_Parent):
    """
    Parent class for modeling total betting
    """

    def __init__(self):
        super().__init__()
        self.bet_type = "Total"
        self.bet_value_col = "OU_Close"
        self.bet_ml_col = "OU_Close_ML"
        self.target_col = "Over_Covered"
        self.remove_cols = ["Home_Win", "Home_Covered"]


class ML_Parent(Modeling_Parent):
    """
    Parent class for modeling moneyline betting
    """

    def __init__(self):
        super().__init__()
        self.bet_type = "Moneyline"
        self.bet_value_col = None
        self.bet_ml_col = "Home_ML"
        self.target_col = "Home_Win"
        self.remove_cols = ["Home_Covered", "Over_Covered"]


if __name__ == '__main__':
    x = Modeling_Parent()
    self = x
    x.run()
