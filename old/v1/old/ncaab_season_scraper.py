# ==============================================================================
# File: ncaab_season_scraper.py
# Project: Season_Scrapers
# File Created: Saturday, 2nd May 2020 6:39:03 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 2nd May 2020 7:14:13 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# NCAAB Season scraper, inheriting from espn_season_scraper
# ==============================================================================

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Season_Scrapers.espn_season_scraper import ESPN_Season_Scraper


class NCAAB_Season_Scraper(ESPN_Season_Scraper):
    def __init__(self):
        self.leauge = 'NCAAB'
        self.folder = 'Data/NCAAB'
        self.re_game_link = None  # FIXME


if __name__ == "__main__":
    x = NCAAB_Season_Scraper()
