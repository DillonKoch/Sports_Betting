# ==============================================================================
# File: banker.py
# Project: allison
# File Created: Tuesday, 30th November 2021 9:01:08 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 30th November 2021 9:01:10 pm
# Modified By: Dillon Koch
# -----
#
# -----
# evaluating the bets made in /Data/Agent_Bets and awarding/subtracting money
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Banker:
    def __init__(self):
        pass

    def run(self):  # Run
        pass


if __name__ == '__main__':
    x = Banker()
    self = x
    x.run()
