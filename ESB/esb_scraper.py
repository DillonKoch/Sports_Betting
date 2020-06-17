# ==============================================================================
# File: esb_scraper.py
# Project: ESB
# File Created: Tuesday, 16th June 2020 7:58:09 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 16th June 2020 8:27:16 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraper for Elite Sportsbook pages
# ==============================================================================

import sys
import urllib.request
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def get_sp1(link):
    user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
    headers = {'User-Agent': user_agent, }
    request = urllib.request.Request(link, None, headers)  # The assembled request
    response = urllib.request.urlopen(request)
    a = response.read().decode('utf-8', 'ignore')
    sp = soup(a, 'html.parser')
    return sp


class ESB_Game:
    def __init__(self):
        self.home_team = None
        self.away_team = None
        self.game_time = None
        self.over = None
        self.under = None
        self.home_spread = None
        self.away_spread = None
        self.home_moneyline = None
        self.away_moneyline = None


class ESB_Scraper:
    def __init__(self):
        pass

    def get_event_boxes(self, sp):  # Top Level
        boxes = sp.find_all('div', attrs={'class': 'col-sm-12 eventbox'})
        return boxes

    def _box_time(self, box):  # Specific Helper esb_game_from_box
        time = box.find_all('div', attrs={'class': 'col-xs-12 visible-xs visible-sm'})
        time_str = time[0].get_text()
        time_str = time_str.strip()
        return time_str

    def _box_teams(self, box):  # Specific Helper esb_game_from_box
        teams = box.find_all('span', attrs={'class': 'team-title'})
        teams = [item.get_text() for item in teams]
        return teams

    def esb_game_from_box(self, box):  # Top Level
        esb_game = ESB_Game()
        esb_game.time = self._box_time(box)
        esb_game.home_team, esb_game.away_team = self._box_teams(box)
        return esb_game

    def run(self, link):  # Run
        sp = get_sp1(link)
        boxes = self.get_event_boxes(sp)
        esb_games = [self.esb_game_from_box(box) for box in boxes]
        return esb_games


if __name__ == "__main__":
    link = "https://www.elitesportsbook.com/sports/pro-football-lines-betting/week-1.sbk"
    x = ESB_Scraper()
    self = x
    r = x.run(link)
