# ==============================================================================
# File: model.py
# Project: Modeling
# File Created: Monday, 6th July 2020 6:45:05 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 7th July 2020 8:13:53 am
# Modified By: Dillon Koch
# -----
#
# -----
# File for building models to predict one of the target variables in the PROD data
# ==============================================================================


import sys
from os.path import abspath, dirname

import tensorflow as tf

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.prep_prod import Prep_Prod

physical_devices = tf.config.experimental.list_physical_devices('GPU')
tf.config.experimental.set_memory_growth(physical_devices[0], True)


class Model:
    def __init__(self, league):
        self.league = league

    def load_data(self):
        prep_prod = Prep_Prod(self.league)
        df, target_df = prep_prod.run()
        return df, target_df

    def add_over_column(self):  # Top Level
        # adds a binary 1/0 col to indicate if the over hit or not
        pass

    def add_home_win_col(self):  # Top Level
        # adds binary col to indicate if home team wins or not
        pass

    def run_score_model(self):  # Run
        df, target_df = self.load_data()

    def run_winner_model(self):  # Run
        pass

    def run_over_under_model(self):  # Run
        pass


if __name__ == "__main__":
    x = Model("NFL")
