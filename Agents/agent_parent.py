# ==============================================================================
# File: agent_parent.py
# Project: allison
# File Created: Sunday, 10th April 2022 1:51:42 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 10th April 2022 1:51:42 pm
# Modified By: Dillon Koch
# -----
#
# -----
# parent class for agents
# ==============================================================================


import datetime
import os
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Agent_Parent:
    def __init__(self):
        pass

    def _current_ts(self):  # Global Helper
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def make_load_agent_df(self):  # Top Level
        """
        making the agent betting df if it doesn't exist, or loading it if it does
        """
        path = ROOT_PATH + f"/Data/Agents/{self.league}/{self.agent_type}.csv"
        if os.path.exists(path):
            agent_df = pd.read_csv(path)
        else:
            cols = ['League', "Date", "Home", "Away", "Bet_Type", "Bet", "Prediction", "Bet_Value", "Bet_ML", "Wager", "To_Win", "Outcome", "Profit", "Bet_ts"]
            agent_df = pd.DataFrame(columns=cols)

        return agent_df

    def _get_bet(self, home, away, bet_type, prediction):  # Specific Helper flat_bet
        if bet_type == "Total":
            return "Over" if prediction > 0.5 else "Under"
        else:
            return home if prediction > 0.5 else away

    def _to_win_amount(self, bet_ml, wager):  # Specific Helper  flat_bet
        if bet_ml > 0:
            to_win = wager * (bet_ml / 100)
        else:
            to_win = wager / (abs(bet_ml) / 100)
        return round(to_win, 2)

    def pred_in_agent_bets(self, pred, agent_bets):  # Top Level
        """
        check if the prediction dict is already in agent_bets
        """
        date = pred['Date']
        home = pred['Home']
        away = pred['Away']
        for agent_bet in reversed(agent_bets):
            if agent_bet['Date'] == date and agent_bet['Home'] == home and agent_bet['Away'] == away:
                return True
        return False

    def run(self):  # Run
        pass


if __name__ == '__main__':
    x = Agent_Parent()
    self = x
    x.run()
