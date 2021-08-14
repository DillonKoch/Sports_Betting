# ==============================================================================
# File: espn_game.py
# Project: allison
# File Created: Tuesday, 10th August 2021 9:19:09 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 10th August 2021 9:19:09 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping game data from espn.com
# given
# ==============================================================================

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESPN_Game_Scraper:
    def __init__(self, league):
        pass

    def run(self, sp):  # Run
        pass


if __name__ == '__main__':
    x = ESPN_Game_Scraper()
    self = x
    x.run()
