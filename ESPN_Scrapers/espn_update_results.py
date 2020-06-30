# ==============================================================================
# File: espn_update_results.py
# Project: ESPN_Scrapers
# File Created: Tuesday, 30th June 2020 11:58:42 am
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 30th June 2020 12:01:18 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraper for updating results of games in ESPN_Data folder that have finished or been updated
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.Utility import parse_league


class ESPN_Update_Results:
    """
     Updates the games in ESPN_Data that have been updated or played
    """

    def __init__(self, league):
        self.league = league

    def load_dfs(self):  # Top Level
        pass

    def run(self):  # Run
        pass


if __name__ == "__main__":
    league = parse_league() if False else "NFL"
    x = ESPN_Update_Results(league)
