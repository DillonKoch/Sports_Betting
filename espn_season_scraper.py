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
        self.egs = ESPN_Game_Scraper()

        self.root_path = "/home/allison/Documents/GITHUB/Sports_Betting/"
        self.nba_folder = "Data/NBA"
        self.nfl_folder = "Data/NFL"
        self.ncaaf_folder = "Data/NCAAF"
        self.ncaab_folder = "Data/NCAAB"

    def _make_season_df(self, ncaab=False):
        cols = ["Date", "Home", "Home_Record", "Away", "Away_Record",
                "Home_Score", "Away_Score", "Status", "ESPN_ID"]
        if ncaab:
            cols += ["1st_Half", "2nd_Half"]
        else:
            cols += ["Quarter_1", "Quarter_2", "Quarter_3", "Quarter_4"]

    def _insert_game_to_df(self, df, game):
        game_row = [game.date, game.home_name, game.home_record, game.away_name, game.away_record,
                    game.home_score, game.away_score, game.status, game.]
        df.loc[len(df)] = game_row

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
