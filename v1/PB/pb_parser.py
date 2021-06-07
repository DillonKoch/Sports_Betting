# ==============================================================================
# File: pb_parser.py
# Project: PB
# File Created: Friday, 1st January 2021 12:48:48 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 1st January 2021 8:42:41 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Parses HTML from PointsBet sportsbook found from pb_navigator.py
# ==============================================================================
# run() method is given sp of a bet


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class PB_Parser:
    def __init__(self):
        pass

    def run(self, bet_sp):  # Run
        pass


if __name__ == '__main__':
    x = PB_Parser()
    self = x
    x.run()
