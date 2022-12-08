# ==============================================================================
# File: espn_rosters.py
# Project: allison
# File Created: Wednesday, 7th December 2022 10:34:24 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 7th December 2022 10:34:24 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping roster data from ESPN so I know which players are on which team at certain times
# ==============================================================================


import datetime
import json
import sys
import time
import urllib.request
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Data.db_login import db_cursor


class ESPN_Rosters:
    def __init__(self, league):
        self.league = league
        self.scraped_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.db, self.cursor = db_cursor()

    def load_roster_links(self):  # Top Level
        """
        loading links to a team's roster page on ESPN and returning team name
        """
        path = ROOT_PATH + f"/Data/Teams/{self.league}.json"
        with open(path, 'r') as f:
            teams_dict = json.load(f)

        # * extracting all the team roster links from the json
        teams = list(teams_dict['Teams'].keys())
        roster_links = [teams_dict['Teams'][team]['Roster'] for team in teams]
        return roster_links, teams

    def _get_sp1(self, link):  # Specific Helper  scrape_roster
        """
        scraping the HTML from a website
        """
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(link, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)
        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
        time.sleep(5)
        return sp

    def _new_row_to_db(self, new_row):  # Specific Helper scrape_roster
        self.cursor.execute("USE sports_betting;")
        sql = f"""INSERT INTO ESPN_Rosters_{self.league} (Team, Player, Player_ID, scrape_ts)
                  VALUES ("{new_row[0]}", "{new_row[1]}", {new_row[2]}, "{new_row[3]}");"""
        self.cursor.execute(sql)

    def scrape_roster(self, roster_link, team):  # Top Level
        """
        scrapes the roster from each roster_link to a dataframe
        """
        sp = self._get_sp1(roster_link)
        table_sp = sp.find('div', attrs={'class': 'Wrapper Card__Content'})
        player_sps = table_sp.find_all('tr', attrs={'class': 'Table__TR Table__TR--lg Table__even'})
        for player_sp in player_sps:
            name_section_sp = player_sp.find_all('td', attrs={'class': 'Table__TD'})[1]
            name_sp = name_section_sp.find('a', attrs={'class': 'AnchorLink'})
            player = name_sp.get_text()
            player_link = name_sp['href']
            player_id = player_link.split('/')[-2]
            new_row = [team, player, player_id, self.scraped_ts]
            self._new_row_to_db(new_row)
        self.db.commit()

    def run(self):  # Run
        roster_links, teams = self.load_roster_links()
        for i, (roster_link, team) in enumerate(zip(roster_links, teams)):
            print(f"{i} - {team} - {roster_link}")
            try:
                self.scrape_roster(roster_link, team)
            except Exception as e:
                print(f"{roster_link} failed with {e}")
                time.sleep(10)


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        x = ESPN_Rosters(league)
        self = x
        x.run()
