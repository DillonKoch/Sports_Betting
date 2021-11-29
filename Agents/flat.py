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


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Agents.agent_parent import Agent_Parent


class Flat(Agent_Parent):
    def __init__(self, league):
        super().__init__()
        self.league = league
        self.agent_name = "flat"

    def run(self):  # Run
        # load bets df
        # load predictions
        # decide how much to wager, if at all based on predictions
        bet_df = self.make_load_bets_df()
        bet_df.to_csv(self.bet_df_path, index=False)


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        x = Flat(league)
        x.run()
