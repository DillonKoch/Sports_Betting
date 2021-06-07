# ==============================================================================
# File: make_bet.py
# Project: Personal_Bets
# File Created: Tuesday, 28th July 2020 11:37:45 am
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 28th July 2020 8:33:59 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for making a new personal bet
# ==============================================================================

import sys
from os.path import abspath, dirname

import pandas as pd
from wandb import init

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Bet_Tracker:
    """
    class for tracking bets made by a person or betting agent
    """

    def __init__(self, bettor):
        self.bettor = bettor.replace(" ", "_")
        self.df_path = ROOT_PATH + "/Personal_Bets/Data/{}.csv".format(self.bettor)

    def load_data(self):  # Top Level
        try:
            df = pd.read_csv(self.df_path)
            return df
        except BaseException:
            print("no data for this bettor!")

    def run(self):  # Run
        df = self.load_data()


if __name__ == "__main__":
    x = Bet_Tracker("Dillon Koch")
    df = x.load_data()
