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

from Modeling.modeling_parent import Modeling_Parent


class NBA_Spread(Modeling_Parent):
    def __init__(self):
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

    def run(self):  # Run
        print("-" * 50)
        print("NBA SPREAD")
        print("-" * 50)
        # * loading data, baseline models
        avg_df_home_away_date = self.load_avg_df(['Home_Covered'], extra_cols=['Home', 'Away', 'Date'])
        raw_df = self.load_raw_df()
        self.model_baseline_avg_points(avg_df_home_away_date, raw_df)


if __name__ == '__main__':
    x = NBA_Spread()
    self = x
    df = x.run()
