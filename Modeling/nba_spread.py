# ==============================================================================
# File: nba_spread.py
# Project: allison
# File Created: Saturday, 23rd October 2021 10:02:32 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 23rd October 2021 10:02:33 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Modeling NBA spread bets
# ==============================================================================

import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_parent import Spread_Parent


class NBA_Spread(Spread_Parent):
    def __init__(self):
        super().__init__()
        self.league = "NBA"

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

        self.plot_confusion_matrix(preds, labels, 'NBA Line')
        self.evaluation_metrics(preds, labels)
        self.spread_total_expected_return(preds, labels)

    # def run(self):  # Run
    #     print("-" * 50)
    #     print("NBA SPREAD")
    #     print("-" * 50)
    #     # * loading data, baseline models
    #     avg_df_home_away_date = self.load_avg_df(['Home_Covered'], extra_cols=['Home', 'Away', 'Date'])
    #     raw_df = self.load_raw_df()
    #     self.model_baseline_avg_points(avg_df_home_away_date, raw_df)

    def run(self, df, alg, num_past_games, player_stat_bool):
        finished_games_df, upcoming_games_df = self.split_finished_upcoming_games(df)
        train_df, test_df = self.split_train_test_df(finished_games_df)
        balanced_train_df = self.balance_classes(train_df)

        train_X, train_y, scaler = self.scaled_X_y(balanced_train_df)
        test_X, test_y, _ = self.scaled_X_y(test_df, scaler)

        model_method = self.model_method_dict[alg]
        model = model_method(train_X, test_X, train_y, test_y)

        if len(upcoming_games_df) > 0:
            upcoming_games_X, _, _ = self.scaled_X_y(upcoming_games_df, scaler=scaler)
            self.make_preds(model, upcoming_games_df, upcoming_games_X, alg, num_past_games, player_stat_bool)
        self.make_preds(model, test_df, test_X, alg, num_past_games, player_stat_bool)


if __name__ == '__main__':
    x = NBA_Spread()
    self = x
    df = x.run_all()
