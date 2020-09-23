# ==============================================================================
# File: wh_general_scraper.py
# Project: Sports_Betting
# File Created: Tuesday, 22nd September 2020 5:02:19 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 22nd September 2020 8:15:04 pm
# Modified By: Dillon Koch
# -----
#
# -----
# General scraper for each of the 3 types of bets (Game Lines, Game Props, Futures)
# ==============================================================================

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class WH_General_Scraper:
    def __init__(self, league):
        pass

    def run(self):  # Run
        pass


if __name__ == '__main__':
    x = WH_General_Scraper()
    self = x
    x.run()
