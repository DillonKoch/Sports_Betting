# ==============================================================================
# File: ncaab_spread.py
# Project: allison
# File Created: Saturday, 23rd October 2021 10:13:03 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 23rd October 2021 10:13:03 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Modeling NCAAB spread bets
# ==============================================================================

import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_parent import Spread_Parent


class NCAAB_Spread(Spread_Parent):
    def __init__(self):
        super().__init__()
        self.league = "NCAAB"

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

        self.plot_confusion_matrix(preds, labels, 'NCAAB Line')
        self.evaluation_metrics(preds, labels)
        self.spread_total_expected_return(preds, labels)

    def run(self, df, alg, num_past_games, player_stat_bool):  # Run
        finished_games_df, upcoming_games_df = self.split_finished_upcoming_games(df)
        train_df, test_df = self.split_train_test_df(finished_games_df)
        balanced_train_df = self.balance_classes(train_df)

        train_X, train_y, scaler = self.scaled_X_y(balanced_train_df)
        test_X, test_y, _ = self.scaled_X_y(test_df, scaler)

        model_method = self.model_method_dict[alg]
        model = model_method(train_X, test_X, train_y, test_y)

        upcoming_games_X, _, _ = self.scaled_X_y(upcoming_games_df, scaler=scaler)
        self.make_preds(model, upcoming_games_df, upcoming_games_X, alg, num_past_games, player_stat_bool)
        self.make_preds(model, test_df, test_X, alg, num_past_games, player_stat_bool)


if __name__ == '__main__':
    x = NCAAB_Spread()
    self = x
    df = x.run_all()
