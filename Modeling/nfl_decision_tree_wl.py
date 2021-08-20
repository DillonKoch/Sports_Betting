# ==============================================================================
# File: nfl_decision_tree_wl.py
# Project: allison
# File Created: Thursday, 19th August 2021 10:17:10 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 19th August 2021 10:17:10 pm
# Modified By: Dillon Koch
# -----
#
# -----
# using Decision Trees to model the winner of NFL games
# ==============================================================================


from os.path import abspath, dirname
import sys

from sklearn.tree import DecisionTreeRegressor

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Data_Cleaning.train_data import Train_Data


class NFL_DT_WL:
    def __init__(self):
        self.train_data = Train_Data("NFL")

    def run(self):  # Run
        model = DecisionTreeRegressor(random_state=18)
        X, y = self.train_data.run()


if __name__ == '__main__':
    x = NFL_DT_WL()
    self = x
    x.run()
