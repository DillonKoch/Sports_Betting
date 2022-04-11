# ==============================================================================
# File: threshold.py
# Project: allison
# File Created: Sunday, 28th November 2021 10:39:05 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 28th November 2021 10:39:06 pm
# Modified By: Dillon Koch
# -----
#
# -----
# agent making bets when models are confident past a certain threshold
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Agents.agent_parent import Agent_Parent


class Threshold(Agent_Parent):
    """
    makes a $5 bet on every bet where the top 10 models agree past a certain threshold
    """

    def __init__(self, league, threshold):
        super().__init__()
        self.league = league
        self.threshold = threshold
        self.thresh_desc = f"_{threshold*100}"
        self.agent_name = "threshold"

    def make_bets(self, agent_bet_df, bet_type, game, top_model_pred_dfs, top_applicable_models):  # Top Level
        models_acc, models_ev, models_pred = self._model_acc_ev_pred(top_applicable_models, top_model_pred_dfs)
        bet_val, bet_ml = self._bet_val_ml(top_model_pred_dfs)
        wager = 5
        to_win = self._to_win(wager, bet_ml)

        # TODO determine if we even make a bet

        new_row = [game[2], game[0], game[1], bet_type, models_acc, models_ev, models_pred,
                   bet_val, bet_ml, wager, to_win, None, None, None, self._current_ts()]
        agent_bet_df.loc[len(agent_bet_df)] = new_row
        return agent_bet_df


if __name__ == '__main__':
    for league in ['NFL']:
        print(league)
        for threshold in [0.55, 0.6, 0.65, 0.7]:
            x = Threshold(league, threshold)
            x.run(prod=True)
