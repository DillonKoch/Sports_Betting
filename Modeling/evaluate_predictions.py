# ==============================================================================
# File: evaluate_predictions.py
# Project: allison
# File Created: Monday, 29th November 2021 9:33:17 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 29th November 2021 9:33:18 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Evaluating the models' performance (accuracy, expected value, etc)
# ==============================================================================


import copy
import datetime
import itertools
import os
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Evaluate_Performance:
    def __init__(self, league, test_preds):
        self.league = league
        self.test_preds = test_preds
        self.test_prod_str = "Test" if test_preds else "Prod"
        self.eval_df_path = ROOT_PATH + f"/Data/Performance/{self.league}/{self.test_prod_str}_model_evals.csv"

    def make_load_eval_df(self):  # Top Level
        """
        makes (if it doesn't exist) or loads the df of model evaluations
        """
        if os.path.exists(self.eval_df_path):
            df = pd.read_csv(self.eval_df_path)
        else:
            eval_df_cols = ['Bet_Type', 'Algorithm', 'Player_Stats', 'Avg_Past_Games', 'Dataset', 'Threshold', 'Bets',
                            'Accuracy', 'Expected_Value', "Eval_ts"]
            df = pd.DataFrame(columns=eval_df_cols)
        return df

    def get_model_combos(self, predictions_df):  # Top Level
        """
        makes a list of the model combinations (bet type, algo, player_stats, # prev games, train/test split, etc)
        """
        bet_types = ['Total', 'Spread', 'Moneyline']
        algorithms = ['logistic regression', 'random forest', 'svm', 'neural net']
        avg_past_games = [3, 5, 10, 15, 20, 25]
        player_stats = [False, True]
        datasets = ['recent_20pct_test']
        return list(itertools.product(bet_types, algorithms, player_stats, avg_past_games, datasets))

    def get_model_df(self, predictions_df, model_combo, thresh):  # Top Level
        """
        finds the subset of the whole predictions_df for the given model_combo
        """
        bet_type, algo, player_stat_bool, avg_past_games, dataset = model_combo
        df = copy.deepcopy(predictions_df)
        df = df.loc[df['Bet_Type'] == bet_type]
        df = df.loc[df['Algorithm'] == algo]
        df = df.loc[df['Avg_Past_Games'] == avg_past_games]
        df = df.loc[df['Player_Stats'] == player_stat_bool]
        df = df.loc[df['Dataset'] == dataset]
        df = df.loc[(df['Prediction'] >= thresh) | (df['Prediction'] <= 1 - thresh)]
        return df

    def _moneyline_profit_per_dollar(self, ml):  # Specific Helper model_expected_value
        """
        returning how much you'd make on a certain ML by betting $1
        """
        if ml < 0:
            profit = 100 / abs(ml)
        else:
            profit = ml / 100
        return profit

    def model_expected_value(self, model_df):  # Top Level
        """
        computes the expected value for every dollar bet on a given model_df
        """
        moneylines = list(model_df['Bet_ML'])
        outcomes = list(model_df['Outcome'])
        # * if no predictions, return None instead of 0
        if len([outcome for outcome in outcomes if not np.isnan(outcome)]) == 0:
            return None
        profits = 0
        for moneyline, outcome in zip(moneylines, outcomes):
            if outcome == 0:
                profits -= 1
            elif outcome == 1:
                profits += self._moneyline_profit_per_dollar(moneyline)
        return round(profits / len(moneylines), 3)

    def _current_ts(self):  # Specific Helper update_eval_df
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def update_eval_df(self, eval_df, model_df, model_combo, thresh, acc, expected_value):  # Top Level
        """
        updates the eval_df with the new accuracy and expected value for a model
        """
        # eval_df_cols = ['Bet_Type', 'Algorithm', 'Player_Stats', 'Avg_Past_Games', 'Dataset', 'Threshold',
        #                 'Accuracy', 'Expected_Value']
        bet_type, algo, player_stat_bool, avg_past_games, dataset = model_combo
        num_bets = len(model_df)
        new_row = [bet_type, algo, player_stat_bool, avg_past_games, dataset, thresh, num_bets, acc, expected_value, self._current_ts()]
        eval_df.loc[len(eval_df)] = new_row
        eval_df.sort_values(by=['Bet_Type', 'Expected_Value'], inplace=True, ascending=False)
        return eval_df

    def run(self):  # Run
        predictions_df = pd.read_csv(ROOT_PATH + f"/Data/Predictions/{self.league}/{self.test_prod_str}_Predictions.csv")
        eval_df = self.make_load_eval_df()
        model_combos = self.get_model_combos(predictions_df)
        for model_combo in tqdm(model_combos):
            for thresh in [0.5, 0.55, 0.6, 0.65, 0.7]:
                model_df = self.get_model_df(predictions_df, model_combo, thresh)
                model_df = model_df.loc[model_df['Bet_ML'].astype(str) != '-10.0']  # ! REMOVE
                acc = round(model_df['Outcome'].mean(), 4)
                expected_value = self.model_expected_value(model_df) if len(model_df) > 0 else None
                eval_df = self.update_eval_df(eval_df, model_df, model_combo, thresh, acc, expected_value)
        eval_df.to_csv(ROOT_PATH + f"/Data/Modeling_Eval/{self.league}/{self.test_prod_str}_models.csv", index=False)
        print("Models evaluated!")


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        # for league in ['NFL']:
        for tp in [False, True]:
            x = Evaluate_Performance(league, tp)
            self = x
            x.run()
