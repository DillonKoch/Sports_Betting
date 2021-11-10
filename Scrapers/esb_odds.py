# ==============================================================================
# File: esb_odds.py
# Project: allison
# File Created: Thursday, 14th October 2021 10:16:57 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 14th October 2021 10:17:24 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraping the Spread, Moneyline, Over/Under from Elite Sportsbook
# ==============================================================================

import datetime
import os
import re
import sys
import time
from os.path import abspath, dirname

import pandas as pd
from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def mfloat(val):
    if val is None:
        return None
    else:
        return float(val)


class ESB_Odds:
    def __init__(self, league):
        self.league = league
        link_dict = {"NFL": "https://www.elitesportsbook.com/sports/pro-football-game-lines-betting/full-game.sbk",
                     "NBA": "https://www.elitesportsbook.com/sports/nba-betting/game-lines-full-game.sbk",
                     "NCAAF": "https://www.elitesportsbook.com/sports/ncaa-football-betting/game-lines-full-game.sbk",
                     "NCAAB": "https://www.elitesportsbook.com/sports/ncaa-men's-basketball-betting/game-lines-full-game.sbk"}
        self.link = link_dict[league]

        self.df_cols = ["Title", "datetime", "Game_Time", "Home", "Away", "Over", "Over_ML",
                        "Under", "Under_ML", "Home_Spread", "Home_Spread_ML", "Away_Spread", "Away_Spread_ML",
                        "Home_ML", "Away_ML", "scraped_ts"]
        self.scrape_ts = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def start_selenium(self):  # Top Level
        """
        fires up the selenium window to start scraping
        """
        options = Options()
        options.headless = True
        self.driver = webdriver.Firefox(executable_path=ROOT_PATH + "/Scrapers/geckodriver", options=options)
        time.sleep(1)

    def load_df(self):  # Top Level
        """
        load the df from /Data/ESB/{league}/Game_Lines.csv
        """
        path = ROOT_PATH + f"/Data/ESB/{self.league}/Game_Lines.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
        else:
            df = pd.DataFrame(columns=self.df_cols)
        return df

    def get_soup_sp(self):  # Top Level
        """
        saves the selenium window's current page as a beautifulsoup object
        """
        html = self.driver.page_source
        sp = soup(html, 'html.parser')
        return sp

    def get_date_events(self, sp):  # Top Level
        """
        Finding all the dates and events on the odds page
        - every event's date is the most recent one in this list
        """
        event_sp = sp.find_all('div', attrs={'class': 'row event'})[0]
        date_events = event_sp.find_all('div', attrs={'class': ['row event', 'col-xs-12 date']})
        return date_events

    def check_is_date(self, date_event, date):  # Top Level
        """
        checking if the date_event is a date (as opposed to an event)
        if so, it returns the date, and found_date is True
        otherwise, it returns the most recent date and found_date is False
        """
        found_date = False
        date_comp = re.compile(
            r"^(January|February|March|April|June|July|August|September|October|November|December|) \d{1,2}, \d{4}$")

        full_text = date_event.get_text()
        match = re.match(date_comp, full_text)
        if match:
            date = datetime.datetime.strptime(full_text, "%B %d, %Y")
            found_date = True

        if date is None:
            raise ValueError("Did not find a date before games!")

        return date, found_date

    def _game_time(self, event):  # Helping Helper _date_event_to_row
        """
        finds the game time of an event
        """
        time = event.find_all('div', attrs={'id': 'time'})
        time = time[0].get_text()
        time_comp = re.compile(r"\d{2}:\d{2} C(S|D)T")
        match = re.search(time_comp, time)
        return match.group(0) if match is not None else None

    def _teams(self, event):  # Helping Helper _date_event_to_row
        """
        finds the home and away teams in an event
        - tie not used right now but is there in some sports
        """
        away = event.find_all('span', attrs={'id': ['firstTeamName', 'awayTeamName']})
        away = away[0].get_text()
        home = event.find_all('span', attrs={'id': ['secondTeamName', 'homeTeamName']})
        home = home[0].get_text()
        tie = event.find_all('span', attrs={'id': 'tie'})
        tie = tie[0].get_text() if len(tie) > 0 else None
        return home, away, tie

    def _moneylines_match(self, text):  # Helping Helper _moneylines
        """
        returns the moneyline if it matches the correct format, else None
        """
        ml_comp = re.compile(r"(((\+|-)\d+)|(even))")
        match = re.match(ml_comp, text)

        if match is None:
            print("No match for ", text)
            return None
        else:
            ml = match.group(1)
            return ml

    def _moneylines(self, event):  # Helping Helper _date_event_to_row
        """
        finds the home/away moneylines of an event
        - the html of ESB labels the totals as moneylines and moneylines as totals
        """
        moneylines = event.find_all('div', attrs={'class': 'column total pull-right'})
        ml_texts = [item.get_text().strip() for item in moneylines]
        away_text = ml_texts[0]
        home_text = ml_texts[1]
        tie_text = ml_texts[2] if len(ml_texts) >= 3 else None

        away_ml = self._moneylines_match(away_text)
        home_ml = self._moneylines_match(home_text)
        tie_ml = self._moneylines_match(tie_text) if tie_text is not None else None

        home_ml = '100' if home_ml == 'even' else home_ml
        away_ml = '100' if away_ml == 'even' else away_ml
        tie_ml = '100' if tie_ml == 'even' else tie_ml
        return mfloat(home_ml), mfloat(away_ml), mfloat(tie_ml)

    def _spreads_match(self, text):  # Helping Helper _spreads
        """
        returns the spread and its moneyline if it matches the correct format, else None
        """
        spread_comp = re.compile(r"^((\+|-)?\d+\.?\d?)\((((\+|-)\d+)|(even))\)$")
        match = re.match(spread_comp, text)
        if match is None:
            print("No match for ", text)
            return None, None
        else:
            spread = match.group(1)
            spread_ml = match.group(3)
            return spread, spread_ml

    def _spreads(self, event):  # Helping Helper _date_event_to_row
        """
        finds the home/away spread/spread_ml of an event
        """
        spreads = event.find_all('div', attrs={'class': 'column spread pull-right'})
        if len(spreads) == 0:
            return tuple([None] * 6)
        spreads_texts = [item.get_text().strip() for item in spreads]
        away_text = spreads_texts[0]
        home_text = spreads_texts[1]
        tie_text = spreads_texts[2] if len(spreads_texts) >= 3 else None

        away_spread, away_spread_ml = self._spreads_match(away_text)
        home_spread, home_spread_ml = self._spreads_match(home_text)
        tie_spread, tie_spread_ml = self._spreads_match(tie_text) if tie_text is not None else None, None

        home_spread_ml = '100' if home_spread_ml == 'even' else home_spread_ml
        away_spread_ml = '100' if away_spread_ml == 'even' else away_spread_ml
        tie_spread_ml = '100' if tie_spread_ml == 'even' else tie_spread_ml

        return (mfloat(home_spread), mfloat(home_spread_ml), mfloat(away_spread), mfloat(away_spread_ml),
                mfloat(tie_spread), mfloat(tie_spread_ml))

    def _totals_match(self, text):  # Helping Helper _totals
        """
        returns the total and its moneyline if it matches the correct format, else None
        """
        total_comp = re.compile(r"(O|U) (\d+\.?\d?)\((((\+|-)\d+)|(even))\)")
        match = re.search(total_comp, text)
        if match is None:
            print("No match for ", text)
            return (None, None)
        else:
            total = match.group(2)
            ml = match.group(3)
            return total, ml

    def _totals(self, event):  # Helping Helper _date_event_to_row
        """
        finds the over/under totals for an event
        the html of ESB labels the totals as moneylines and moneylines as totals
        """
        totals = event.find_all('div', attrs={'class': 'column money pull-right'})
        totals_texts = [item.get_text().strip() for item in totals]
        over_text = totals_texts[0]
        under_text = totals_texts[1]
        tie_text = totals_texts[2] if len(totals_texts) >= 3 else None

        over, over_ml = self._totals_match(over_text)
        under, under_ml = self._totals_match(under_text)
        tie, tie_ml = (None, None) if tie_text is None else self._totals_match(tie_text)

        over_ml = '100' if over_ml == 'even' else over_ml
        under_ml = '100' if under_ml == 'even' else under_ml
        tie_ml = '100' if tie_ml == 'even' else tie_ml
        return mfloat(over), mfloat(over_ml), mfloat(under), mfloat(under_ml), mfloat(tie), mfloat(tie_ml)

    def date_event_to_row(self, date_event, date):  # Top Level
        """
        converts a date_event and date to a new row in the dataframe
        """
        game_time = self._game_time(date_event)
        home, away, _ = self._teams(date_event)
        home_ml, away_ml, _ = self._moneylines(date_event)
        home_spread, home_spread_ml, away_spread, away_spread_ml, _, _ = self._spreads(date_event)
        over, over_ml, under, under_ml, _, _ = self._totals(date_event)

        row = ['Full Game', date, game_time, home, away,
               over, over_ml, under, under_ml,
               home_spread, home_spread_ml, away_spread, away_spread_ml,
               home_ml, away_ml,
               self.scrape_ts]
        return row

    def save_df(self, df):  # Top Level
        """
        saves the dataframe to /Data/ESB/{league}/Game_Lines.csv
        """
        df['datetime'] = pd.to_datetime(df['datetime'])
        df.to_csv(ROOT_PATH + f"/Data/ESB/{self.league}/Game_Lines.csv", index=False)

    def run(self):  # Run
        # * printing for logs
        print('-' * 50)
        print(self.scrape_ts)
        print(self.league)

        # * starting selenium and loading df
        self.start_selenium()
        self.driver.get(self.link)
        df = self.load_df()

        # * going through dates and events to update df with current odds
        date_events = self.get_date_events(self.get_soup_sp())
        date = None
        for date_event in date_events:
            date, found_date = self.check_is_date(date_event, date)
            if found_date:
                continue

            row = self.date_event_to_row(date_event, date)
            df.loc[len(df)] = row

        # * saving df, exiting selenium
        self.save_df(df)
        self.driver.quit()
        print('-' * 50)


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        x = ESB_Odds(league)
        self = x
        sp = x.run()
