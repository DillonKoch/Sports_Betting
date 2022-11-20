# ==============================================================================
# File: wh_game_scraper.py
# Project: WH
# File Created: Saturday, 29th August 2020 5:17:52 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 8th September 2020 9:56:27 am
# Modified By: Dillon Koch
# -----
#
# -----
# Game scraper for william hill sportsbook
# https://stackoverflow.com/questions/7867537/how-to-select-a-drop-down-menu-value-with-selenium-using-python
# https://selenium-python.readthedocs.io/locating-elements.html
# ==============================================================================


import re
import sys
import time
from os.path import abspath, dirname

import pandas as pd
from bs4 import BeautifulSoup as soup
from selenium import webdriver
import datetime
import numpy as np


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from WH.wh_base_scraper import WH_Base_Scraper
from WH.wh_game_prop_scraper import Game_Prop_Scraper
from Utility.merge_odds_dfs import merge_odds_dfs
from Utility.Utility import parse_league


class WH_Game:
    """
    class for representing a single game from William Hill Sportsbook
    """

    def __init__(self):
        self.title = None
        self.datetime = None
        self.game_time = None
        self.home_team = None
        self.away_team = None
        self.over = None
        self.over_ml = None
        self.under = None
        self.under_ml = None
        self.home_line = None
        self.home_line_ml = None
        self.away_line = None
        self.away_line_ml = None
        self.home_ml = None
        self.away_ml = None
        self.scraped_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def create_datetime(self):  # Run
        """
        Uses the web-scraped game_time string to create a datetime object
        - WH gives something like "Sep 1 | 4:30pm"
        - if the game month is less than the current month, I add 1 to the year
          this ensures the correct year if I run scraping Dec 31 for a game Jan 1
        """
        if self.game_time is None:
            raise ValueError("self.game_time is not populated!")

        dt = datetime.datetime.strptime(self.game_time, "%b %d | %I:%M%p")
        today = datetime.date.today()
        year = today.year
        if dt.month < today.month:
            year += 1
            print("changing year for this game to {}-------".format(year))
        dt = dt.replace(year=year)
        print(dt)
        self.datetime = dt

    def to_row(self):  # Run
        row = [self.title, self.datetime, self.game_time, self.home_team, self.away_team,
               self.over, self.over_ml, self.under, self.under_ml,
               self.home_line, self.home_line_ml, self.away_line, self.away_line_ml,
               self.home_ml, self.away_ml, self.scraped_ts]
        return row


class WH_Game_Scraper(WH_Base_Scraper):
    def __init__(self, league, bet_name):
        self.league = league
        self.bet_name = bet_name

        sport = "football" if self.league in ["NFL", "NCAAF"] else "basketball"
        self.today_link = "https://www.williamhill.com/us/nj/bet/{}/events/today".format(sport)
        self.all_link = "https://www.williamhill.com/us/nj/bet/{}/events/all".format(sport)

        self.more_bets_links = []
        self.odds_cols = ['Over_WH', 'Over_ml_WH', 'Under_WH', 'Under_ml_WH', 'Home_Line_WH',
                          'Home_Line_ml_WH', 'Away_Line_WH', 'Away_Line_ml_WH', 'Home_ML_WH',
                          'Away_ML_WH']

    def create_games_df(self):  # Top Level
        cols = ["Title", "datetime", "Game_Time", "Home", "Away", "Over_WH", "Over_ml_WH",
                "Under_WH", "Under_ml_WH", "Home_Line_WH", "Home_Line_ml_WH",
                "Away_Line_WH", "Away_Line_ml_WH", "Home_ML_WH", "Away_ML_WH", "scraped_ts"]
        return pd.DataFrame(columns=cols)

    def get_all_leagues_sp(self, link):  # Top Level
        """
        given a link for games today or all games, this method will expand all the league dropdowns
        and return the sp with all game information
        - link to great stackoverflow post in header
        """
        driver = webdriver.Firefox(executable_path=r'/home/allison/Documents/geckodriver')
        driver.get(link)

        # while there are still leagues to expand, we'll expand them
        try:
            while True:
                driver.find_element_by_xpath("//div[@class='expanderHeader collapsed']").click()
                time.sleep(3)
                for i in range(15):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)
        except BaseException:
            print("No more leagues to expand")

        html = driver.page_source
        sp = soup(html, 'html.parser')
        driver.close()
        return sp

    def find_league_section(self, sp):  # Top Level
        """
        finds all the league sections, then once it finds a match with self.league, will
        return only the section for the current league we care about
        """
        league_sections = sp.find_all('div', attrs={'class': 'Expander has--toggle competitionExpander'})
        for section in league_sections:
            league_name = section.find_all('span', attrs={'class': 'title'})[0].get_text()
            print(f"Found section for league: {league_name}")
            if league_name == self.league:
                return section

        print(f"Could not find a section for league: {self.league}!")

    def get_event_game_time(self, game, event):  # Specific Helper update_df
        """
        finds the game date and time from an event (game)
        """
        date = event.find_all('div', attrs={'class': 'dateContainer'})
        game_time = date[0].get_text()
        print(f"game time: {game_time}")
        game.game_time = game_time
        return game

    def get_event_teams(self, game, event):  # Specific Helper update_df
        """
        finds the teams playing in an event
        """
        teams = event.find_all('span', attrs={'class': 'truncate2Rows'})
        teams = [item.get_text() for item in teams]
        away_name, home_name = teams
        print(f"Home: {home_name}")
        print(f"Away: {away_name}")
        game.home_team = home_name
        game.away_team = away_name
        return game

    def get_event_lines(self, game, event):  # Specific Helper update_df
        """
        finds the lines (found in col 2) for an event
        """
        col2_header = event.find_all('div', attrs={'class': 'header selectionHeader truncate3Rows col2'})
        print(col2_header[0].get_text())

        line_ml_comp = re.compile(r"^(((\+|\-)\d+.\d+)|(PICK))((\+|\-)\d+)$")
        lines = event.find_all('div', attrs={'class': 'selectionContainer col2'})
        lines = [item.get_text().strip() for item in lines]

        away_line = re.search(line_ml_comp, lines[0]).group(1)
        away_line_ml = re.search(line_ml_comp, lines[0]).group(5)

        home_line = re.search(line_ml_comp, lines[1]).group(1)
        home_line_ml = re.search(line_ml_comp, lines[1]).group(5)

        print(f"home line: {home_line} ({home_line_ml})")
        print(f"away line: {away_line} ({away_line_ml})")
        game.home_line = home_line
        game.home_line_ml = home_line_ml
        game.away_line = away_line
        game.away_line_ml = away_line_ml
        return game

    def get_event_moneylines(self, game, event):  # Specific Helper get_event_moneylines
        """
        finds the moneylines (found in col 3) for an event
        """
        col3_header = event.find_all('div', attrs={'class': 'header selectionHeader truncate3Rows col3'})
        print(col3_header[0].get_text())

        moneylines = event.find_all('div', attrs={'class': 'selectionContainer col3'})
        if len(moneylines) == 0:
            print("No Moneylins found!")
            home_ml = "NL"
            away_ml = "NL"
        else:
            away_ml, home_ml = [item.get_text().strip() for item in moneylines]

        print(f"home moneyline: {home_ml}")
        print(f"away moneyline: {away_ml}")
        game.home_ml = home_ml
        game.away_ml = away_ml
        return game

    def get_event_totals(self, game, event):  # Specific Helper update_df
        """
        finds the totals (over unders, in col 4) for an event
        """
        col4_header = event.find_all('div', attrs={'class': 'header selectionHeader truncate3Rows col4'})
        print(col4_header[0].get_text())

        totals = event.find_all('div', attrs={'class': 'selectionContainer col4'})
        totals = [item.get_text() for item in totals]
        if totals == ['', '']:
            over_amount, over_total_ml, under_amount, under_total_ml = ["NL"] * 4
        else:
            total_comp = re.compile(r"^(Over|Under)  (\d+.\d+)((\-|\+)\d+)$")
            over_label = re.search(total_comp, totals[0]).group(1)
            assert over_label == "Over"
            over_amount = re.search(total_comp, totals[0]).group(2)
            over_total_ml = re.search(total_comp, totals[0]).group(3)

            under_label = re.search(total_comp, totals[1]).group(1)
            assert under_label == "Under"
            under_amount = re.search(total_comp, totals[1]).group(2)
            under_total_ml = re.search(total_comp, totals[1]).group(3)

        print(f"Over: {over_amount} ({over_total_ml})")
        print(f"Under: {under_amount} ({under_total_ml})")
        game.over = over_amount
        game.over_ml = over_total_ml
        game.under = under_amount
        game.under_ml = under_total_ml
        return game

    def get_num_prop_bets(self, event):  # Specific Helper new_partial_df
        footer = event.find_all('div', attrs={'class': 'footer'})[0]
        num_prop_str = footer.find_all('strong')
        if len(num_prop_str) > 0:
            num_props = num_prop_str[0].get_text()
            num_props = int(num_props)
            print(f"Found {num_props} prop bets!")
        else:
            print("No prop bets found!")
            num_props = 0
        return num_props

    def get_event_more_bets_link(self, event):  # Specific Helper update_df
        """
        finds the "more bets" link of an event to scrape prop bets
        """
        base_link = "https://www.williamhill.com"
        more_bets_link = event.find_all('div', attrs={'class': 'footer'})
        more_bets_link = more_bets_link[0].find_all(href=True)
        more_bets_link = more_bets_link[0]['href']
        more_bets_link = base_link + more_bets_link
        print(more_bets_link)
        return more_bets_link

    def _scrape_game_props(self, more_bets_link, game):  # Specific Helper new_partial_df
        # goal is to pull in a different scraper to update data with props here
        print('will scrape props here...')
        prop_scraper = Game_Prop_Scraper(self.league, more_bets_link, game.datetime,
                                         game.home_team, game.away_team)
        df = prop_scraper.run()
        print("Scraped props!")

    def new_partial_df(self, today=True):  # Top Level
        """
        Creates a new df from scratch with bets from all games in
        either the "today" or "all" section
        """
        new_df = self.create_games_df()
        link = self.today_link if today else self.all_link
        sp = self.get_all_leagues_sp(link)
        league_section = self.find_league_section(sp)
        if league_section is None:
            return new_df
        events = league_section.find_all('div', attrs={'class': 'eventContainer'})
        for event in events:
            game = WH_Game()
            game.title = self.league
            print('-' * 100)
            game = self.get_event_game_time(game, event)
            if "live" in game.game_time.lower():  # skipping live odds (for now)
                print('skipping live game...')
                continue
            game.create_datetime()
            game = self.get_event_teams(game, event)
            game = self.get_event_lines(game, event)
            game = self.get_event_moneylines(game, event)
            game = self.get_event_totals(game, event)
            new_df.loc[len(new_df)] = game.to_row()

            num_prop_bets = self.get_num_prop_bets(event)
            if num_prop_bets > 0:
                more_bets_link = self.get_event_more_bets_link(event)
                self._scrape_game_props(more_bets_link, game)
        return new_df

    def _clean_types(self, df):  # Specific Helper create_new_df
        """
        making all the numeric columns as type 'float'
        - scraping gives results like +3.5 for the spread, which causes errors when it's
          saved to a csv, then reloaded as just 3.5 (screws up removing duplicates)
        """
        for col in self.odds_cols:
            df[col] = df[col].replace("NL", np.nan)
            df[col] = df[col].astype(float)
        return df

    def create_new_df(self):  # Run
        """
        creates df's with games shown in the "today" and "all" sections,
        combines them and drops duplicates
        - returns df of all games shown on the site right now
        """
        today_df = self.new_partial_df(today=True)
        all_df = self.new_partial_df(today=False)
        full_df = pd.concat([today_df, all_df])
        full_df.drop_duplicates(subset=['datetime', 'Home', 'Away'], inplace=True)
        return full_df

    def update_df(self):  # Run
        csv_path = ROOT_PATH + f"/WH/Data/{self.league}/Game_Lines.csv"
        new_df = self.create_new_df()
        try:
            old_df = pd.read_csv(csv_path)
        except FileNotFoundError:
            new_df.to_csv(csv_path, index=False)
            print(f"Created a new file for {self.league} game lines!")
            return new_df

        old_df = self._clean_types(old_df)
        new_df = self._clean_types(new_df)

        drop_cols = ['datetime', 'Home', 'Away']
        odds_cols = ['Game_Time', 'Home', 'Away', 'Over_WH', 'Over_ml_WH', 'Under_WH',
                     'Under_ml_WH', 'Home_Line_WH', 'Home_Line_ml_WH', 'Away_Line_WH', 'Away_Line_ml_WH',
                     'Home_ML_WH', 'Away_ML_WH']
        combined_df = merge_odds_dfs(old_df, new_df, drop_cols, odds_cols)
        combined_df.to_csv(csv_path, index=False)
        print("Saved updated data!")
        return combined_df


if __name__ == "__main__":
    league = parse_league()
    # league = "NBA"
    x = WH_Game_Scraper(league, "Game_Lines")
    self = x
    df = x.update_df()
