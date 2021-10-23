# ==============================================================================
# File: nfl_ml.py
# Project: allison
# File Created: Friday, 22nd October 2021 11:18:50 am
# Author: Dillon Koch
# -----
# Last Modified: Friday, 22nd October 2021 11:18:51 am
# Modified By: Dillon Koch
# -----
#
# -----
# modeling NFL MoneyLine bets
# ==============================================================================


import sys
from os.path import abspath, dirname

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.modeling_parent import Modeling_Parent


class NFL_ML(Modeling_Parent):
    def __init__(self):
        self.league = "NFL"

    def model_baseline_favored_team(self, raw_df):  # Top Level
        """
        baseline model for predicting ML's that just picks the favored team every time
        """
        raw_df = self.add_home_favored_col(raw_df)
        preds = raw_df['Home_Favored']
        labels = raw_df['Home_Win']
        home_mls = raw_df['Home_ML']
        away_mls = raw_df['Away_ML']
        self.plot_confusion_matrix(preds, labels, "NFL MoneyLine (1=Home Win)")
        self.evaluation_metrics(preds, labels)
        self.moneyline_expected_return(preds, labels, home_mls, away_mls)

    def run(self):  # Run
        raw_df = self.load_raw_df()

        self.model_baseline_favored_team(raw_df)


if __name__ == '__main__':
    x = NFL_ML()
    self = x
    x.run()
