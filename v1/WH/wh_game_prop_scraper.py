# ==============================================================================
# File: wh_game_prop_scraper.py
# Project: Sports_Betting
# File Created: Wednesday, 2nd September 2020 4:37:17 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 4th September 2020 5:57:43 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraper for prop bets associated with a game
# ==============================================================================


import datetime
import sys
import time
from os.path import abspath, dirname

import pandas as pd
from bs4 import BeautifulSoup as soup


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.merge_odds_dfs import merge_odds_dfs
from Utility.selenium_scraper import Selenium_Scraper


class Game_Prop_Scraper:
    def __init__(self, league, link, datetime, home, away):
        self.league = league
        self.link = link
        self.datetime = datetime
        self.home = home
        self.away = away

    def _get_scraped_ts(self):  # Global Helper
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def create_df(self):  # Top Level
        """
        creates blank df for adding game props from all sections/leagues
        """
        cols = ["datetime", "Home", "Away", "Section", "Subsection", "Bet", "Spread/overunder",
                "Odds", "scraped_ts"]
        return pd.DataFrame(columns=cols)

    def _selected_section_name(self, sp):  # Specific Helper get_section_sp_list
        selected_section = sp.find_all('li', attrs={'class': 'listButton collectionItem selected'})
        section = selected_section[0].get_text()
        time.sleep(3)
        return section

    def get_section_sp_list(self, ss, include_popular=False):  # Top Level
        """
        Clicks through the different prop sections with selenium, and returns a list
        of each section's sp and name
        """
        first_sp = soup(ss.driver.page_source, 'html.parser')
        first_name = self._selected_section_name(first_sp)
        sp_section_list = [(first_sp, first_name)]

        elements = ss.driver.find_elements_by_xpath("//li[@class='listButton collectionItem']")
        for element in elements:
            element.click()
            current_sp = soup(ss.driver.page_source, 'html.parser')
            section_name = self._selected_section_name(current_sp)
            # if section_name == "Popular":
            #     if not include_popular:
            #         continue
            sp_section_list.append((current_sp, section_name))
            time.sleep(2)
        sp_section_list = [pair for pair in sp_section_list if pair[1] != "Popular"]
        return sp_section_list

    def _get_bets(self, bet_list):  # Specific Helper add_section_bets
        """
        add_section_bets scrapes the "truncateText" tag, which gives inconsistent results
        - this method takes the results and separates them into two items that are easily
          inserted into the dataframe in the spread/overunder and odds columns
        """
        len_bet_list = len(bet_list)
        if len_bet_list == 1:
            return None, bet_list[0].get_text()
        elif len_bet_list == 2:
            item1 = bet_list[0].get_text()
            item1 = item1.replace("Over ", "").replace("Under ", "")
            return item1, bet_list[1].get_text()
        elif len_bet_list == 0:
            return None, None

    def add_section_bets(self, sp, df, section_name):  # Top Level
        """
        Given the sp of one prop bet section, this method adds all the bets inside
        the section to the ongoing dataframe
        """
        scraped_ts = self._get_scraped_ts()
        subsections = sp.find_all('div', attrs={'class': 'MarketCard'})
        for subsection in subsections:
            try:
                subsection_name = subsection.find_all('span', attrs={'class': 'title'})[0].get_text()
                outcomes = subsection.find_all('div', attrs={'class': 'outcome'})
                for outcome in outcomes:
                    bet = outcome.find_all('div', attrs={'class': 'outcomeTitle'})
                    bet = bet[0].get_text() if len(bet) > 0 else None
                    odds = outcome.find_all('div', attrs={'class': 'truncateText'})
                    ou_spread, ml = self._get_bets(odds)
                    df.loc[len(df)] = [self.datetime, self.home, self.away, section_name,
                                       subsection_name, bet, ou_spread, ml, scraped_ts]
            except Exception as e:
                print("ERROR, ", e)
        return df

    def _clean_types(self, df):  # Specific Helper run
        """
        cleaning the old_df and newly scraped df data types to be consistent to
        avoid merging errors
        """
        num_cols = ['Spread/overunder', 'Odds']
        for col in num_cols:
            df[col] = df[col].astype(float)
        return df

    def run(self):  # Run
        df = self.create_df()

        # get sp of first prop section to show up
        ss = Selenium_Scraper(self.link, [])
        ss.driver.implicitly_wait(10)
        ss.driver.get(ss.start_link)
        # time.sleep(8)

        # adding bets from each prop section
        section_sps = self.get_section_sp_list(ss)
        for pair in section_sps:
            sp, section_name = pair
            df = self.add_section_bets(sp, df, section_name)
        ss.driver.close()

        # loading the old df (if it exists) or saving the new one
        old_df_path = ROOT_PATH + f"/WH/Data/{self.league}/Game_Props.csv"
        try:
            old_df = pd.read_csv(old_df_path)
        except FileNotFoundError:
            print("No df")
            df.to_csv(old_df_path, index=False)
            return df

        # cleaning and merging the old/new dataframes and saving
        drop_cols = ['datetime', 'Home', 'Away', 'Section', 'Subsection', 'Bet']
        odds_cols = ['Section', 'Subsection', 'Bet', 'Spread/overunder', 'Odds']
        old_df = self._clean_types(old_df)
        df = self._clean_types(df)
        full_df = merge_odds_dfs(old_df, df, drop_cols, odds_cols)
        full_df.to_csv(old_df_path, index=False)

        return full_df


if __name__ == "__main__":
    link = 'https://www.williamhill.com/us/nj/bet/basketball/BE_EVdab1e016-f6e3-4390-ba0b-ab4e7f13475d/milwaukee-bucks-at-miami-heat'
    link = 'https://www.williamhill.com/us/nj/bet/football/BE_EVd76d9347-601c-483a-bca3-8c3d340ee826/middle-tennessee-blue-raiders-at-army-black-knights'
    link = 'https://www.williamhill.com/us/nj/bet/football/BE_EV7115ce3f-98ed-4147-9aea-834379e813e8/uab-blazers-at-miami-fl-hurricanes'
    dt = datetime.date.today()
    home = "TEST"
    away = "TEST2"
    x = Game_Prop_Scraper("NCAAF", link, dt, home, away)
    self = x
    x.run()
