# ==============================================================================
# File: run_models.py
# Project: Modeling
# File Created: Monday, 13th July 2020 1:36:54 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 13th July 2020 1:57:15 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# File for running all the models in a league to make predictions, save/email results
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Run_Models:
    def __init__(self, league: str):
        self.league = league

    def create_df(self):  # Top Level
        pass

    def run(self):  # Run
        pass


if __name__ == "__main__":
    x = Run_Models("NFL")

# this is a new comment let's freaking go mano
    # this is a good comment
