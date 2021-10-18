# ==============================================================================
# File: esb_odds.py
# Project: allison
# File Created: Thursday, 14th October 2021 10:16:57 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 14th October 2021 10:17:24 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraping the Spread, Moneyline, Over/Under from Elite Sportsbook
# ==============================================================================


import sys
import urllib.request
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESB_Odds:
    def __init__(self, league):
        self.league = league
        link_dict = {"NFL": "https://www.elitesportsbook.com/sports/pro-football-game-lines-betting/full-game.sbk",
                     "NBA": "https://www.elitesportsbook.com/sports/nba-betting/game-lines-full-game.sbk",
                     "NCAAF": "https://www.elitesportsbook.com/sports/ncaa-football-betting/game-lines-full-game.sbk",
                     "NCAAB": ""}
        self.link = link_dict[league]

    def get_sp1(self, link):  # Top Level
        """
        scrapes HTML from the link
        """
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(link, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)
        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
        return sp

    def run(self):  # Run
        sp = self.get_sp1(self.link)
        # ! LOOKS LIKE I HAVE TO USE SELENIUM FOR THIS - WON'T GET SP FROM USUAL WAY !
        return sp


if __name__ == '__main__':
    league = "NBA"
    x = ESB_Odds(league)
    self = x
    sp = x.run()
