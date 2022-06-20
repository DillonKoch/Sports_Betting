# ==============================================================================
# File: dynamic.py
# Project: allison
# File Created: Sunday, 10th April 2022 1:56:37 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 10th April 2022 1:56:37 pm
# Modified By: Dillon Koch
# -----
#
# -----
# making dynamic bets where wager depends on prediction confidence
# ==============================================================================

import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Agents.agent_parent import Agent_Parent


class Dynamic(Agent_Parent):
    def __init__(self, league):
        super(Dynamic, self).__init__()
        self.league = league
        self.agent_type = "Dynamic"

    def _dynamic_wager(self, confidence):  # Specific Helper dynamic_bet
        """
        make a bet somewhere between $5 to $15, depending on the confidence level
        """
        min_amount = 5
        extra_confidence = abs(confidence - 0.5) * 20
        return min_amount + extra_confidence

    def dynamic_bet(self, agent_df, pred):  # Top Level
        """
        make a dynamic bet and add it to the agent_df
        """
        date = pred['Date']
        home = pred['Home']
        away = pred['Away']
        bet_type = pred['Bet_Type']
        bet = self._get_bet(home, away, bet_type, pred['Prediction'])
        prediction = pred['Prediction']
        bet_val = pred['Bet_Value']
        bet_ml = pred['Bet_ML']
        wager = self._dynamic_wager(pred['Prediction'])
        to_win = self._to_win_amount(bet_ml, wager)
        new_bet = [self.league, date, home, away, bet_type, bet, prediction, bet_val, bet_ml, wager, to_win, None, None, self._current_ts()]
        agent_df.loc[len(agent_df)] = new_bet
        return agent_df

    def run(self):
        pred_df = pd.read_csv(ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv")
        agent_df = self.make_load_agent_df()
        preds = pred_df.to_dict('records')
        agent_bets = agent_df.to_dict('records')

        for pred in preds:
            if not self.pred_in_agent_bets(pred, agent_bets):
                agent_df = self.dynamic_bet(agent_df, pred)

        agent_df.to_csv(ROOT_PATH + f"/Data/Agents/{self.league}/Dynamic.csv", index=False)


if __name__ == "__main__":
    league = "NBA"
    x = Dynamic(league)
    self = x
    x.run()
