# ==============================================================================
# File: dynamic.py
# Project: allison
# File Created: Sunday, 28th November 2021 10:32:56 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 28th November 2021 10:32:57 pm
# Modified By: Dillon Koch
# -----
#
# -----
# dynamic betting agent that wagers different amounts based on model confidence
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Agents.agent_parent import Agent_Parent


class Dynamic(Agent_Parent):
    """
    makes a bet using an average of the top 10 models
    - the amount wagered is adjusted dynamically based on the confidence of the model
    """

    def __init__(self, league):
        super().__init__()
        self.league = league
        self.agent_name = "dynamic"

    def make_bets(self, agent_bet_df, bet_type, game, top_model_pred_dfs, top_applicable_models):  # Top Level
        models_acc, models_ev, models_pred = self._model_acc_ev_pred(top_applicable_models, top_model_pred_dfs)
        bet_val, bet_ml = self._bet_val_ml(top_model_pred_dfs)
        wager = 2 + (20 * abs(models_pred - 0.5))
        to_win = self._to_win(wager, bet_ml)

        new_row = [game[2], game[0], game[1], bet_type, models_acc, models_ev, models_pred,
                   bet_val, bet_ml, wager, to_win, None, None, None, self._current_ts()]
        agent_bet_df.loc[len(agent_bet_df)] = new_row
        return agent_bet_df


if __name__ == '__main__':
    for league in ['NFL']:
        print(league)
        x = Dynamic(league)
        x.run(prod=True)
