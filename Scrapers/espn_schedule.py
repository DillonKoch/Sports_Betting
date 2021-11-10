# ==============================================================================
# File: espn_schedule.py
# Project: allison
# File Created: Tuesday, 10th August 2021 8:40:29 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 10th August 2021 8:40:30 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping upcoming games for all leagues NFL/NBA/NCAAF/NCAAB
# ==============================================================================

import datetime
import json
import os
import sys
import time
import urllib.request
from os.path import abspath, dirname

import pandas as pd
from bs4 import BeautifulSoup as soup
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESPN_Schedule_Scraper:
    def __init__(self, league):
        self.league = league
        self.cols = ["Game_ID", "Season", "Week"]
        self.league_first_year = {"NFL": 2007, "NBA": 2008, "NCAAF": 2007, "NCAAB": 2008}
        self.df_path = ROOT_PATH + f"/Data/ESPN/{league}/Games.csv"

    def load_df(self):  # Top Level
        """
        loads the Games.csv dataframe if it exists, or creates a blank one
        """
        if os.path.exists(self.df_path):
            return pd.read_csv(self.df_path)
        return pd.DataFrame(columns=self.cols)

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
        adds the seasontype part for NBA games - 1=preseason, 2=regular season, 3=postseason
        """
        new_links = []
        for link in links:
            regular_season_link = link + "seasontype/2"
            postseason_link = link + "seasontype/3"
            new_links.extend([regular_season_link, postseason_link])
        return new_links

    def load_schedule_links(self, scrape_past_years):  # Top Level
        """
        loads all the links to schedules from /Data/Teams/{json file}
        - also adds in other links to past years since 2007 if scrape_past_years is True
        """
        path = ROOT_PATH + f"/Data/Teams/{self.league}_Teams.json"
        with open(path) as f:
            team_dict = json.load(f)
        teams = list(team_dict['Teams'].keys())

        links = [team_dict['Teams'][team]['Schedule'] for team in teams]
        links = self._add_season(links, scrape_past_years)
        links = self._add_season_type(links) if self.league == "NBA" else links
        return links

    def get_sp1(self, link):  # Top Level
        """
        scrapes the HTML from the link
        """
        time.sleep(5)
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(link, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)
        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
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

    def update_df(self, df, data):  # Top Level
        """
        updates the df with new game id's in scraped data
        """
        existing_game_ids = [str(item) for item in list(df['Game_ID'])]
        for game in data:
            game_id = game[0]
            if str(game_id) not in existing_game_ids:
                new_row = [None] * len(list(df.columns))
                new_row[:3] = game
                print('new game')
                df.loc[len(df)] = new_row
        return df

    def run(self, scrape_past_years=False):  # Run
        df = self.load_df()
        schedule_links = self.load_schedule_links(scrape_past_years)
        for schedule_link in tqdm(schedule_links):
            try:
                sp = self.get_sp1(schedule_link)
                table = sp.find('tbody', attrs={'class': 'Table__TBODY'})
                rows = table.find_all('tr')
                rows = self.remove_preseason(rows) if self.league == "NFL" else rows
                season_str = self.season_str(schedule_link)
                data = self.rows_to_data(rows, season_str)
                df = self.update_df(df, data)
                df.to_csv(self.df_path, index=False)
            except Exception as e:
                print(e)
                print(schedule_link)


if __name__ == '__main__':
    league = "NCAAB"
    x = ESPN_Schedule_Scraper(league)
    self = x
    scrape_past_years = False
    x.run(scrape_past_years)
