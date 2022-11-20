# ==============================================================================
# File: espn_team_stats_scraper.py
# Project: ESPN
# File Created: Saturday, 5th September 2020 2:25:24 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 6th September 2020 11:56:06 am
# Modified By: Dillon Koch
# -----
#
# -----
# scraper for getting the team stats from an ESPN game
# ==============================================================================

from os.path import abspath, dirname
import sys
import time
import argparse

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN.espn_team_stats import Team_Stats
from Utility.Utility import get_sp1


class Team_Stats_Scraper:
    def __init__(self, league):
        self.league = league
        self.football_league = True if self.league in ["NFL", "NCAAF"] else False

    @property
    def base_link(self):  # Property
        link_dict = {
            "NFL": "https://www.espn.com/nfl/matchup?gameId=",
            "NBA": "https://www.espn.com/nba/matchup?gameId=",
            "NCAAF": "https://www.espn.com/college-football/matchup?gameId=",
            "NCAAB": "https://www.espn.com/mens-college-basketball/matchup?gameId="
        }
        return link_dict[self.league]

    def get_stats_list(self, sp):  # Top Level
        """
        Scrapes the team stats highights from the sp/html

        these results are in a format like ['FG 24-63 22-47', 'Assists 6 11', ...]
        where the first part is the stat (FG), second is the away team's value (24-63), and
        third is the home team's value (22-47)
        """
        highlights = sp.find_all('tr', attrs={'class': 'highlight'})
        highlights += sp.find_all('tr', attrs={'class': 'indent'})
        results = []
        for item in highlights:
            item = item.get_text()
            item = item.replace('\t', '').replace('\n', ' ')
            for i in range(5):
                item = item.replace('  ', ' ')
            item = item.strip()
            results.append(item)
        return results

    def make_stats_object(self, stats_list):  # Top Level
        """
        uses the stats_list from get_stats_list to create a Team_Stats object for the game
        """
        ts = Team_Stats()
        for stat_string in stats_list:
            if self.football_league:
                ts.add_football_item(stat_string)
            else:
                ts.add_basketball_item(stat_string)
        return ts

    def run(self, espn_id, sp=False):  # Run
        full_link = self.base_link + str(espn_id)
        sp = get_sp1(full_link)
        stats_list = self.get_stats_list(sp)
        team_stats = self.make_stats_object(stats_list)
        time.sleep(5)
        return team_stats


if __name__ == '__main__':
    x = Team_Stats_Scraper("NFL")
    self = x
    espn_id = "401128044"
    ts = x.run(espn_id)
