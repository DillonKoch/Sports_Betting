# ==============================================================================
# File: team_matcher.py
# Project: Utility
# File Created: Sunday, 25th October 2020 7:25:28 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 25th October 2020 7:34:21 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Matches team names to the official ESPN team names
# https://www.datacamp.com/community/tutorials/fuzzy-string-python
# ==============================================================================


import sys
from os.path import abspath, dirname

from fuzzywuzzy import fuzz

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Team_Matcher:
    def __init__(self):
        pass

    def run(self):  # Run
        # load ESPN team names
        # match a new string to an official name from ESPN dict
        pass


if __name__ == '__main__':
    x = Team_Matcher()
    self = x
    x.run()
