# ==============================================================================
# File: ncaab_ml.py
# Project: allison
# File Created: Friday, 22nd October 2021 3:45:01 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 22nd October 2021 3:45:02 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Modeling NCAAB MoneyLine bets
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Modeling.modeling_parent import ML_Parent


class NCAAB_ML(ML_Parent):
    def __init__(self):
        super().__init__()
        self.league = "NCAAB"

    # def model_baseline_favored_team(self, raw_df):  # Top Level
    #     """
    #     baseline model for predicting ML's that just picks the favored team every time
    #     """
    #     raw_df = self.add_home_favored_col(raw_df)
    #     preds = raw_df['Home_Favored']
    #     labels = raw_df['Home_Win']
    #     home_mls = raw_df['Home_ML']
    #     away_mls = raw_df['Away_ML']
    #     self.plot_confusion_matrix(preds, labels, "NCAAB MoneyLine (1=Home Win)")
    #     self.evaluation_metrics(preds, labels)
    #     self.moneyline_expected_return(preds, labels, home_mls, away_mls)


if __name__ == '__main__':
    x = NCAAB_ML()
    self = x
    x.run_all()