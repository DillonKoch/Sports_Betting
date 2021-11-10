# ==============================================================================
# File: nba_total.py
# Project: allison
# File Created: Saturday, 23rd October 2021 10:31:52 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 23rd October 2021 10:31:53 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Modeling NBA total bets
# ==============================================================================

from os.path import abspath, dirname
import sys

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_parent import Modeling_Parent


class NBA_Total(Modeling_Parent):
    def __init__(self):
        self.league = "NBA"

    def model_baseline_avg_points(self, avg_df_home_away_date, raw_df):  # Top Level
        # * left merge avg_df and the Home_Line_Close
        raw_df_home_line = raw_df[['Home', 'Away', 'Date', 'OU_Close']]
        df = pd.merge(avg_df_home_away_date, raw_df_home_line, how='left', on=['Home', 'Away', 'Date'])

        # * make predictions, evaluate
        labels = df['Over_Covered']
        home_pts = df['Home_Final']
        away_pts = df['Away_Final']
        total_pts = home_pts + away_pts
        preds = total_pts > df['OU_Close']

        self.plot_confusion_matrix(preds, labels, 'NBA Line')
        self.evaluation_metrics(preds, labels)
        self.spread_total_expected_return(preds, labels)

    def run(self):  # Run
        print("-" * 50)
        print("NBA TOTAL")
        print("-" * 50)
        # * loading data, baseline models
        avg_df_home_away_date = self.load_avg_df(['Over_Covered'], extra_cols=['Home', 'Away', 'Date'])
        raw_df = self.load_raw_df()
        self.model_baseline_avg_points(avg_df_home_away_date, raw_df)


if __name__ == '__main__':
    x = NBA_Total()
    self = x
    x.run()
