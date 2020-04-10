# ==============================================================================
# File: ESPN_Scraper.py
# Project: Sports_Betting
# File Created: Tuesday, 7th April 2020 7:34:33 am
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 7th April 2020 7:41:07 am
# Modified By: Dillon Koch
# -----
#
#
# -----
# File for scraping game data from ESPN
# ==============================================================================

import urllib
from bs4 import BeautifulSoup as soup


class ESPN_Scrape:
    def __init__(self):
        self.link_dict = {
            "NFL": 'https://www.espn.com/nfl/game/_/gameId/',
            "NCAAF": 'https://www.espn.com/college-football/game/_/gameId/',
            "MLB": 'https://www.espn.com/mlb/game?gameId=',
            "NBA": 'https://www.espn.com/nba/game?gameId=',
            "NCAAB": 'https://www.espn.com/mens-college-basketball/game?gameId=',
            "NHL": 'https://www.espn.com/nhl/game/_/gameId/'
        }

    def get_sp1(self, link):

        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'

        headers = {'User-Agent': user_agent, }

        request = urllib.request.Request(link, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)

        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
        return sp

    def hockey_info(self, game_id):
        """
        hockey_info grabs the game info for NHL games

        Args:
            game_id (int): end of the url for an NHL game on ESPN

        Returns:
            [tuple]: home/away team names, home/away records, "NHL"
        """
        link = self.link_dict["NHL"] + str(game_id)
        sp1 = self.get_sp1(link)

        team_names = sp1.find_all('div', attrs={'class': 'ScoreCell__TeamName ScoreCell__TeamName--displayName truncate db'})
        away_full, home_full = [item.get_text() for item in team_names]

        records = sp1.find_all('div', attrs={'class': 'Gamestrip__Record db n10 clr-gray-04'})
        away_record, home_record = [item.get_text() for item in records]

        return home_full, away_full, home_record, away_record, 'NHL'
