# ==============================================================================
# File: consensus.py
# Project: allison
# File Created: Sunday, 28th November 2021 10:36:13 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 28th November 2021 10:36:13 pm
# Modified By: Dillon Koch
# -----
#
# -----
# consensus agent making bets when all algorithms agree on which side to take
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Agents.agent_parent import Agent_Parent


class Consensus(Agent_Parent):
    def __init__(self, league):
        super().__init__()
        self.league = league
        self.agent_name = "consensus"

    def run(self):  # Run
        """
        makes a bet when the best version of each algorithm agrees
        """
        pass


if __name__ == '__main__':
    x = Consensus()
    self = x
    x.run()
