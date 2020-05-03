# ==============================================================================
# File: nfl_season_scraper.py
# Project: Season_Scrapers
# File Created: Saturday, 2nd May 2020 6:38:44 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 2nd May 2020 7:56:47 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# File for scraping NFL Season data, inheriting from main espn_season_scraper file
# ==============================================================================
import re
from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Season_Scrapers.espn_season_scraper import ESPN_Season_Scraper


class NFL_Season_Scraper(ESPN_Season_Scraper):
    def __init__(self):
        self.league = 'NFL'
        self.folder = 'Data/NFL'
        self.re_game_link = re.compile(r"http://www.espn.com/nfl/game/_/gameId/(\d+)")


if __name__ == "__main__":
    x = NFL_Season_Scraper()
    sections = x._get_game_sections('min', '2019')
