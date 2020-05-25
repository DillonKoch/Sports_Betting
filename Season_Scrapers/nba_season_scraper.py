# ==============================================================================
# File: nba_season_scraper.py
# Project: Season_Scrapers
# File Created: Saturday, 2nd May 2020 6:38:35 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 23rd May 2020 10:56:21 am
# Modified By: Dillon Koch
# -----
#
#
# -----
# File for scraping NBA season data, inheriting from main espn_season_scraper file
# ==============================================================================

import re
import sys
from os.path import abspath, dirname
import time
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Season_Scrapers.espn_season_scraper import ESPN_Season_Scraper
from Season_Scrapers.espn_game_scraper import ESPN_Game_Scraper


class NBA_Season_Scraper(ESPN_Season_Scraper):
    def __init__(self):
        self.league = 'NBA'
        self.folder = 'Data/NBA'
        self.re_game_link = re.compile(r"http://www.espn.com/nba/game\?gameId=(\d+)")
        egs = ESPN_Game_Scraper()
        self.all_game_info_func = egs.all_nba_info


if __name__ == "__main__":
    x = NBA_Season_Scraper()
    sections = x._get_game_sections('mia', '2019')
    links = []
    gameids = []
    for section in sections:
        link, gameid = x._link_gameid_from_section(section)
        links.append(link)
        gameids.append(gameid)

    games = x.team_gameid_links('mia', '2019')

    df = x._make_season_df()
    # df = x._full_season_df('mia', '2020')
    x.run_all_season_scrapes()
