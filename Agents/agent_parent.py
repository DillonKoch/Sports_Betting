# ==============================================================================
# File: agent_parent.py
# Project: allison
# File Created: Sunday, 28th November 2021 10:15:32 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 28th November 2021 10:15:33 pm
# Modified By: Dillon Koch
# -----
#
# -----
# parent class for betting agents
# ==============================================================================


import os
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Agent_Parent:
    def __init__(self):
        self.bet_df_cols = ["Date", "Home", "Away", "Bet Type", "Odds", "ML", "Bet", "To Win",
                            "Result"]

    @property
    def bet_df_path(self):  # Property
        return ROOT_PATH + f"/Data/Agent_Bets/{self.league}/{self.agent_name}.csv"

    def make_load_bets_df(self):  # Top Level
        """
        makes/loads the agent's df of bets it has made
        """
        if os.path.exists(self.bet_df_path):
            df = pd.read_csv(self.bet_df_path)
        else:
            df = pd.DataFrame(columns=self.bet_df_cols)
        return df

    def plot_profits(self, agents, start_date, end_date):  # Run
        """
        plotting the profits of agents' bets from start_date to end_date
        """
        pass

    def run(self):  # Run
        pass


if __name__ == '__main__':
    x = Agent_Parent()
    self = x
    x.run()
