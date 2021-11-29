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
    def __init__(self, league):
        super().__init__()
        self.league = league
        self.agent_name = "dynamic"

    def run(self):  # Run
        pass


if __name__ == '__main__':
    x = Dynamic()
    self = x
    x.run()
