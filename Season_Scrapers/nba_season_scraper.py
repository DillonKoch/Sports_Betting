# ==============================================================================
# File: nba_season_scraper.py
# Project: Season_Scrapers
# File Created: Saturday, 2nd May 2020 6:38:35 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 4th May 2020 4:37:24 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# File for scraping NBA season data, inheriting from main espn_season_scraper file
# ==============================================================================

import re
import sys
from os.path import abspath, dirname

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Season_Scrapers.espn_season_scraper import ESPN_Season_Scraper


class NBA_Season_Scraper(ESPN_Season_Scraper):
    def __init__(self):
        self.league = 'NBA'
        self.folder = 'Data/NBA'
        self.re_game_link = re.compile(r"http://www.espn.com/nba/game\?gameId=(\d+)")


if __name__ == "__main__":
    x = NBA_Season_Scraper()
    sections = x._get_game_sections('mia', '2019')
    dates = [x._game_date_from_section(section) for section in sections]
