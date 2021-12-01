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
    def __init__(self, league):
        super().__init__()
        self.league = league
        self.agent_name = "threshold"

    def run(self):  # Run
        """
        makes a $5 bet on every bet where the top 10 models agree past a certain threshold
        """
        pass


if __name__ == '__main__':
    x = Threshold()
    self = x
    x.run()
