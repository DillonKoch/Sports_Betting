# ==============================================================================
# File: espn_season_scraper.py
# Project: Sports_Betting
# File Created: Tuesday, 14th April 2020 5:08:27 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 14th April 2020 5:08:55 pm
# Modified By: Dillon Koch
# -----
#
#
# -----
# Scraper to get all season-long data for each league
# ==============================================================================

from espn_game_scraper import ESPN_Game_Scraper
from Utility import get_sp1
import re


class ESPN_Season_Scraper:
    def __init__(self):
        self.egs = ESPN_Game_Scraper()i

        self.nba_folder =

    def nba_team_game_links(self, team):
        base_link = "https://www.espn.com/nba/team/schedule/_/name/"
        full_link = base_link + team
        sp = get_sp1(full_link)
        table_tds = sp.find_all('td', attrs={'class': 'Table__TD'})
        game_strs = [str(td) for td in table_tds if 'http://www.espn.com/nba/game?gameId=' in str(td)]

        link_comp = re.compile(r'href="http://www.espn.com/nba/game\?gameId=\d+')
        game_links = [link_comp.findall(game_str) for game_str in game_strs]
        game_links = [item[0].replace('href="', '') for item in game_links]

        return game_links


if __name__ == "__main__":
    ess = ESPN_Season_Scraper()
    heat_links = ess.nba_team_game_links('mia')
