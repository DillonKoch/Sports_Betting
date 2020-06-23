# ==============================================================================
# File: esb_prop_scraper.py
# Project: ESB
# File Created: Wednesday, 17th June 2020 6:37:45 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 22nd June 2020 2:35:05 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraper for prop bets on Elite Sportsbook
# ==============================================================================

import sys
import urllib.request
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.Utility import get_sp1


class ESB_Prop:
    def __init__(self):
        self.title = None
        self.description = None
        self.team = None
        self.moneyline = None


class ESB_Prop_Scraper:
    def __init__(self):
        pass

    def get_title_description(self, sp):  # Top Level
        title = sp.find_all('span', attrs={'class': 'titleLabel'})[0].get_text()
        description = sp.find_all('div', attrs={'id': 'futureDescription'})[0].get_text()
        return title, description

    def get_teams(self, sp):
        teams = sp.find_all('span', attrs={'class': 'team'})
        teams = [item.get_text() for item in teams]
        return teams

    def run(self, link):  # Run
        sp = get_sp1(link)
        esb_prop = ESB_Prop()
        esb_prop.title, esb_prop.description = self.get_title_description(sp)
        return esb_prop


if __name__ == "__main__":
    x = ESB_Prop_Scraper()
    link = "https://www.elitesportsbook.com/sports/nba-betting/futures-2020-nba-championship.sbk"
    self = x
    r = x.run(link)
