# ==============================================================================
# File: ncaaf_ml.py
# Project: allison
# File Created: Friday, 22nd October 2021 3:39:54 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 22nd October 2021 3:40:03 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Modeling NCAAF MoneyLine bets
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Modeling.modeling_parent import Modeling_Parent


class NCAAF_ML(Modeling_Parent):
    def __init__(self):
        self.league = "NCAAF"

    def model_baseline_favored_team(self, raw_df):  # Top Level
        """
        baseline model for predicting ML's that just picks the favored team every time
        """
        raw_df = self.add_home_favored_col(raw_df)
        preds = raw_df['Home_Favored']
        labels = raw_df['Home_Win']
        home_mls = raw_df['Home_ML']
        away_mls = raw_df['Away_ML']
        self.plot_confusion_matrix(preds, labels, "NCAAF MoneyLine (1=Home Win)")
        self.evaluation_metrics(preds, labels)
        self.moneyline_expected_return(preds, labels, home_mls, away_mls)

    def run(self):  # Run
        raw_df = self.load_raw_df(['Home_ML', 'Away_ML'])

        self.model_baseline_favored_team(raw_df)


if __name__ == '__main__':
    x = NCAAF_ML()
    self = x
    x.run()
