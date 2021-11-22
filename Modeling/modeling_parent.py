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
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Modeling_Parent:
    def __init__(self):
        self.model_method_dict = {"logistic regression": self.model_logistic_regression,
                                  "random forest": self.model_random_forest,
                                  "svm": self.model_svm,
                                  "neural net": self.model_neural_net}

    def model_logistic_regression(self):  # Top Level
        pass  # Done

    def model_random_forest(self):  # Top Level
        pass  # Done

    def model_svm(self):  # Top Level
        pass  # Done

    def model_neural_net(self):  # Top Level
        pass  # Done

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

    def split_train_test(self, X, y):  # Top Level
        """
        """
        train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=18)
        return train_X, val_X, train_y, val_y

    def _make_load_df(self):  # Specific Helper make_preds
        """
        loads the predictions file for the league if it exists, otherwise makes it
        """
        path = ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
        else:
            df = pd.DataFrame(columns=["Game_Date", "Home", "Away", "Bet_Type", "Bet_Value",
                                       "Bet_ML", "Prediction", "Outcome", "Algorithm",
                                       "Avg_Past_Games", "Player_Stats", "Pred_ts"])
        return df

    def _current_ts(self):  # Specific Helper  make_preds
        """returning a string of the current time"""
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def make_preds(self, model, upcoming_games_df, upcoming_games_X, alg, avg_past_games, player_stats_bool):  # Top Level
        """
        making predictions on upcoming games and saving to /Data/Predictions/
        """
        df = self._make_load_df()
        preds = model.predict_proba(upcoming_games_X)
        for i in range(len(upcoming_games_df)):
            game_row = upcoming_games_df.iloc[i, :]
            prediction = round(preds[i][1], 3)
            new_row = [game_row['Date'], game_row['Home'], game_row['Away'], self.bet_type,
                       game_row[self.bet_value_col], game_row[self.bet_ml_col],
                       prediction, None, alg, avg_past_games, player_stats_bool, self._current_ts()]
            df.loc[len(df)] = new_row
        df.to_csv(ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv", index=False)
        print("Predictions saved!")

    def run_all(self):  # Run
        """
        running all algorithms on all datasets
        """
        algs = ['logistic regression', 'svm', 'random forest', 'neural net']
        num_past_games = [3, 5, 10, 15, 20, 25]
        player_stats_bools = [False, True]
        for alg in algs:
            for npg in num_past_games:
                for player_stat_bool in player_stats_bools:
                    ps_str = "with" if player_stat_bool else "without"
                    print(f"{self.league} {self.bet_type} {alg} on past {npg} games {ps_str} player stats")
                    df = self.load_df(past_games=npg, player_stats=player_stat_bool)
                    self.run(df, alg, npg, player_stat_bool)


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

    def _expected_return_thresh(self, preds, labels, thresh):  # Specific Helper expected_return
        """
        computing the expected return when only placing on bets that the model
          is at least 'thresh' % confident on
        - thresh is the decimal pct for model confidence (0.6 -> model has to be >=60% confident)
        """
        assert (thresh >= 0.5) and (thresh <= 1.0), "thresh must be between 0.5 and 1.0"
        home_cover_preds = [item[1] for item in preds]
        thresh_preds = []
        thresh_labels = []
        for pred, label in zip(home_cover_preds, list(labels)):
            if abs(pred - 0.5) > (thresh - 0.5):
                thresh_preds.append(pred)
                thresh_labels.append(label)

        return np.array(thresh_preds), np.array(thresh_labels)

    def expected_return(self, preds, labels, thresh=0.5):  # Top Level
        preds, labels = self._expected_return_thresh(preds, labels, thresh)
        binary_preds = np.array([1 if pred >= 0.5 else 0 for pred in preds])
        num_bets = len(binary_preds)
        correct = (binary_preds == labels).sum()
        incorrect = num_bets - correct
        total_winnings = (correct * (10 / 11)) - incorrect
        expected_return_on_dollar = total_winnings / num_bets
        print(f"Won/Lost {round(total_winnings,2)} on {num_bets} bets at {thresh} threshold, for {round(expected_return_on_dollar, 2)} expected return per dollar")
        return total_winnings


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

    def expected_return(self):  # Top Level
        pass


if __name__ == '__main__':
    x = Modeling_Parent()
    self = x
    x.run()
