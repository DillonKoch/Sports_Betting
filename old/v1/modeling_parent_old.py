# ==============================================================================
# File: modeling_parent.py
# Project: allison
# File Created: Friday, 22nd October 2021 9:52:38 am
# Author: Dillon Koch
# -----
# Last Modified: Friday, 22nd October 2021 9:52:38 am
# Modified By: Dillon Koch
# -----
#
# -----
# Parent class for all the modeling files
# ==============================================================================

import sys
from os.path import abspath, dirname

import pandas as pd
import seaborn as sns
from sklearn.metrics import (accuracy_score, confusion_matrix, f1_score,
                             mean_absolute_error)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_data import Modeling_Data


class Modeling_Parent:
    def __init__(self):
        pass

    def load_raw_df(self, non_null_cols=[]):  # Top Level
        """
        loading the raw dataframe from /Data/{league}.csv
        - has the stats from each game, not averages from past n games
        - used for baseline models depending on betting odds
        """
        path = ROOT_PATH + f"/Data/{self.league}.csv"
        df = pd.read_csv(path)
        for col in non_null_cols:
            df = df[df[col].notnull()]
        return df

    def load_avg_df(self, targets, extra_cols=[]):  # Top Level
        """
        uses Modeling_Data() to build a dataset with avg stats from the last n games
        - used most frequently for modeling, since it has no data leakage
        - eligible targets: "Home Covered",
        """
        modeling_data = Modeling_Data(self.league)
        df = modeling_data.run(targets, extra_cols)
        return df

    def split_avg_df(self, avg_df, targets):  # Top Level
        """
        runs train_test_split on avg_df
        """
        y = avg_df[targets]
        X = avg_df[[col for col in list(avg_df.columns) if col not in targets]]
        train_X, val_X, train_y, val_y = train_test_split(X, y, random_state=18)
        return train_X, val_X, train_y, val_y

    def balance_classes(self, df, target_col):  # Top Level
        """
        balancing the dataframe to include an even amount of training examples
        for each of the target column's outputs (assumes target col is binary)
        # TODO could add some resampling so we don't throw data away
        """
        positive_data = df[df[target_col] == 1]
        positive_data.reset_index(inplace=True, drop=True)
        negative_data = df[df[target_col] == 0]
        negative_data.reset_index(inplace=True, drop=True)
        lower_class = min([len(positive_data), len(negative_data)])
        balanced_df = pd.concat([positive_data.iloc[:lower_class], negative_data.iloc[:lower_class]])
        balanced_df.reset_index(inplace=True, drop=True)
        return balanced_df

    def scale_cols(self, X):  # Top Level
        """
        applying the standard scaler to all the columns in X
        """
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        return X

    def add_home_favored_col(self, raw_df):  # Top Level
        """
        adds a binary column to raw_df from /Data/{league}.csv indicating if the home team is favored or not
        """
        # * adding Home_Win column
        raw_df['Home_Win'] = raw_df['Home_Final'] > raw_df['Away_Final']
        raw_df['Home_Win'] = raw_df['Home_Win'].astype(int)
        # * adding Home_Favored column
        raw_df['Home_Favored'] = raw_df['Home_ML'] < 0
        raw_df['Home_Favored'] = raw_df['Home_Favored'].astype(int)
        return raw_df

    def plot_confusion_matrix(self, preds, labels, title):  # Top Level
        """
        plots a confusion matrix given binary predictions and labels
        """
        cf_matrix = confusion_matrix(labels, preds)
        sns.heatmap(cf_matrix, annot=True, fmt="g", cmap='Blues').set_title(title)

    def evaluation_metrics(self, preds, labels):  # Top Level
        """
        given predictions and labels, this method computes various evaluation metrics
        """
        mae = mean_absolute_error(labels, preds)
        print(f"Mean absolute error: {mae}")
        acc = accuracy_score(labels, preds)
        print(f"Accuracy: {round(acc*100, 2)}%")
        cm = confusion_matrix(labels, preds)
        print(cm)
        f1 = f1_score(labels, preds)
        print(f"F1 score: {f1}")

    def moneyline_expected_return(self, preds, labels, home_mls, away_mls):  # Top Level
        """
        computes the expected return for every dollar bet on a moneyline bet
        """
        winnings = []
        for pred, label, home_ml, away_ml in zip(list(preds), list(labels), list(home_mls), list(away_mls)):
            pred_correct = pred == label
            if pred_correct:
                ml = home_ml if pred == 1 else away_ml
                if ml > 0:
                    winnings.append(ml / 100)
                else:
                    winnings.append(1 / abs((ml / 100)))
            else:
                winnings.append(-1)

        total_winnings = sum(winnings)
        num_bets = len(preds)
        expected_return_on_dollar = total_winnings / num_bets
        print(f"Won/Lost {round(total_winnings,2)} on {num_bets} bets, for {round(expected_return_on_dollar,2)} expected return per dollar")

    def spread_total_expected_return(self, preds, labels):  # Top Level
        """
        computes the expected return for every dollar bet on spread/total bets at -110
        """
        num_bets = len(preds)
        correct = (preds == labels).sum()
        incorrect = num_bets - correct
        total_winnings = (correct * (10 / 11)) - incorrect
        expected_return_on_dollar = total_winnings / num_bets
        print(f"Won/Lost {round(total_winnings,2)} on {num_bets} bets, for {round(expected_return_on_dollar, 2)} expected return per dollar")
        return total_winnings

    def run(self):  # Run
        pass


if __name__ == '__main__':
    x = Modeling_Parent()
    self = x
    x.run()
