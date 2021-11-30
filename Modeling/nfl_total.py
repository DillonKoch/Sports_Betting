# ==============================================================================
# File: nfl_total.py
# Project: allison
# File Created: Saturday, 23rd October 2021 10:14:51 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 23rd October 2021 10:14:52 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Modeling NFL total bets
# ==============================================================================

import sys
from os.path import abspath, dirname

from sklearn import svm
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_parent import Total_Parent


class NFL_Total(Total_Parent):
    def __init__(self):
        super().__init__()
        self.league = "NFL"

    # def model_baseline_avg_points(self, avg_df_home_away_date, raw_df):  # Top Level
    #     # * left merge avg_df and the Home_Line_Close
    #     raw_df_home_line = raw_df[['Home', 'Away', 'Date', 'OU_Close']]
    #     df = pd.merge(avg_df_home_away_date, raw_df_home_line, how='left', on=['Home', 'Away', 'Date'])

    #     # * make predictions, evaluate
    #     labels = df['Over_Covered']
    #     home_pts = df['Home_Final']
    #     away_pts = df['Away_Final']
    #     total_pts = home_pts + away_pts
    #     preds = total_pts > df['OU_Close']

    #     self.plot_confusion_matrix(preds, labels, 'NBA Line')
    #     self.evaluation_metrics(preds, labels)
    #     self.spread_total_expected_return(preds, labels)

    def model_baseline(self):  # Top Level
        pass

    def model_neural_net(self, train_X, val_X, train_y, val_y):  # Top Level
        pass


if __name__ == '__main__':
    x = NFL_Total()
    self = x
    x.run_all()
