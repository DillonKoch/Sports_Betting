# ==============================================================================
# File: flat.py
# Project: allison
# File Created: Sunday, 28th November 2021 10:18:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 28th November 2021 10:18:48 pm
# Modified By: Dillon Koch
# -----
#
# -----
# agent that makes simple flat bets using model predictions
# ==============================================================================


import sys
from os.path import abspath, dirname


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Agents.agent_parent import Agent_Parent


class Flat(Agent_Parent):
    def __init__(self, league):
        super().__init__()
        self.league = league
        self.agent_name = "flat"

    def make_bets(self, agent_bet_df, bet_type, game, top_model_pred_dfs, top_applicable_models):  # Top Level
        """
        makes a flat $5 bet on everything, based on the top 10 models' predictions
        """
        models_acc, models_ev, models_pred = self._model_acc_ev_pred(top_applicable_models, top_model_pred_dfs)
        bet_val, bet_ml = self._bet_val_ml(top_model_pred_dfs)
        wager = 5
        to_win = self._to_win(wager, bet_ml)

        new_row = [game[2], game[0], game[1], bet_type, models_acc, models_ev, models_pred,
                   bet_val, bet_ml, wager, to_win, None, None, None, self._current_ts()]
        agent_bet_df.loc[len(agent_bet_df)] = new_row
        return agent_bet_df


if __name__ == '__main__':
    for league in ['NFL']:
        print(league)
        x = Flat(league)
        x.run(prod=True)
