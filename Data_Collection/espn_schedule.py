# ==============================================================================
# File: espn_schedule.py
# Project: allison
# File Created: Saturday, 26th November 2022 5:08:27 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 26th November 2022 5:08:28 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping ESPN game ID's from teams' schedules on ESPN
# ==============================================================================

import datetime
import json
import sys
import time
import urllib.request
from os.path import abspath, dirname
import random

from bs4 import BeautifulSoup as soup
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Data.db_login import db_cursor


class ESPN_Schedule_Scraper:
    def __init__(self, league):
        self.league = league
        self.league_first_year = {"NFL": 2007, "NBA": 2008, "NCAAF": 2007, "NCAAB": 2008}
        self.db, self.cursor = db_cursor()
        self.num_nulls = 68 if self.league in ['NFL', 'NCAAF'] else 60

    def _add_season(self, links, scrape_past_years=False):  # Specific Helper load_schedule_links
        """
        adds the season part of the string
        """
        start_year = self.league_first_year[self.league] if scrape_past_years else int(datetime.datetime.now().year) - 1
        end_year = int(datetime.datetime.now().year) + 2

        new_links = []
        for year in list(range(start_year, end_year, 1)):
            for link in links:
                new_link = link + f"/season/{year}/"
                new_links.append(new_link)
        return new_links

    def _add_season_type(self, links):  # Specific Helper load_schedule_links
        """
        adds the seasontype part for NBA games - 1=preseason, 2=regular season, 3=postseason, 5=play-in-season (NBA)
        """
        new_links = []
        for link in links:
            regular_season_link = link + "seasontype/2"
            postseason_link = link + "seasontype/3"
            play_in_link = link + "seasontype/5"
            new_link_list = [regular_season_link, postseason_link]
            if self.league == "NBA":
                new_link_list.append(play_in_link)
            new_links.extend(new_link_list)
        return new_links

    def load_schedule_links(self, scrape_past_years):  # Top Level
        """
        loads all the links to schedules from /Data/Teams/{json file}
        - also adds in other links to past years since 2007 if scrape_past_years is True
        """
        path = ROOT_PATH + f"/Data/Teams/{self.league}.json"
        with open(path) as f:
            team_dict = json.load(f)
        teams = list(team_dict['Teams'].keys())

        links = [team_dict['Teams'][team]['Schedule'] for team in teams]
        links = self._add_season(links, scrape_past_years)
        links = self._add_season_type(links) if self.league == "NBA" else links
        return links

    def get_sp1(self, link):
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(link, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)
        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
        time.sleep(5)
        return sp

    def remove_preseason(self, rows):  # Top Level
        """
        NFL schedules show preseason on the same page as regular/postseason
        going through each row and throwing out the preseason
        """
        new_rows = []
        include_row = False
        for row in rows:
            row_text = row.get_text()
            if row_text in ['Regular Season', 'Postseason']:
                include_row = True
            elif row_text == 'Preseason':
                include_row = False

            if include_row:
                new_rows.append(row)
        return new_rows

    def season_str(self, schedule_link):  # Top Level
        """
        uses the schedule url to create the season string in format 2007-08
        """
        url_season = int(schedule_link.split('/season/')[1].split('/')[0])
        season_start = url_season if league in ['NFL', 'NCAAF'] else url_season - 1
        season_end = season_start + 1
        season_str = f"{season_start}-{str(season_end)[2:]}"
        return season_str

    def rows_to_data(self, rows, season_str):  # Top Level
        """
        converts rows from schedule table into data to be saved in the csv
        """
        data = []
        for row in rows:
            row_link_sps = row.find_all('a', attrs={'class': 'AnchorLink'}, href=True)
            row_links = [row_link_sp['href'] for row_link_sp in row_link_sps]
            new_game_links = [row_link for row_link in row_links if '/gameId/' in row_link]
            if len(new_game_links) > 0:
                new_game_id = new_game_links[0].split('/')[-1]
                tds = row.find_all('td', attrs={'class': 'Table__TD'})
                new_game_week = tds[0].get_text() if league == "NFL" else None
                data.append([new_game_id, season_str, new_game_week])
        return data

    def data_to_db(self, data):  # Top Level
        self.cursor.execute("USE sports_betting;")
        table = f"ESPN_Games_{self.league}"
        cols_sql = f"""SELECT COLUMN_NAME
                       FROM information_schema.columns
                       WHERE TABLE_NAME = N'{table}';"""
        self.cursor.execute(cols_sql)
        cols = [item[0] for item in self.cursor]
        col_names = "(" + ", ".join(cols) + ")"

        for row in data:
            row = [f'"{item}"' for item in row]
            new_row = row + ['"1997-11-02"', '"Kennedy Cougars"', row[0]] + (["NULL"] * self.num_nulls)
            vals = "(" + ", ".join(new_row) + ")"
            insert_sql = f"INSERT IGNORE INTO {table} {col_names} VALUES {vals};"
            self.cursor.execute(insert_sql)
        self.db.commit()

    def run(self, scrape_past_years=False):  # Run
        schedule_links = self.load_schedule_links(scrape_past_years)
        for schedule_link in tqdm(schedule_links):
            try:
                sp = self.get_sp1(schedule_link)
                table = sp.find('tbody', attrs={'class': 'Table__TBODY'})
                rows = table.find_all('tr')
                rows = self.remove_preseason(rows) if self.league == "NFL" else rows
                season_str = self.season_str(schedule_link)
                data = self.rows_to_data(rows, season_str)
                self.data_to_db(data)
            except Exception as e:
                print(e)
                print(schedule_link)


if __name__ == '__main__':
    for league in ['NBA', 'NCAAF', 'NCAAB']:
        x = ESPN_Schedule_Scraper(league)  # TODO set to False / update somehow
        self = x
        x.run(True)
