# ==============================================================================
# File: ncaaf_season_scraper.py
# Project: Season_Scrapers
# File Created: Saturday, 2nd May 2020 6:38:54 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 9th May 2020 9:20:06 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# NCAAF Season scraper, inheriting from main espn_season_scraper
# ==============================================================================


from os.path import abspath, dirname
import sys
import re

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Season_Scrapers.espn_season_scraper import ESPN_Season_Scraper


class NCAAF_Season_Scraper(ESPN_Season_Scraper):
    def __init__(self):
        self.league = 'NCAAF'
        self.folder = 'Data/NCAAF'
        self.re_game_link = re.compile(r"http://www.espn.com/college-football/game/_/gameId/(\d+)")


if __name__ == "__main__":
    x = NCAAF_Season_Scraper()
    sections = x._get_game_sections("228", "2019")
