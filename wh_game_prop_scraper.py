# ==============================================================================
# File: wh_game_prop_scraper.py
# Project: Sports_Betting
# File Created: Wednesday, 2nd September 2020 4:37:17 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 2nd September 2020 6:04:53 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraper for prop bets associated with a game
# ==============================================================================


import sys
from os.path import abspath, dirname
import time

import pandas as pd
from bs4 import BeautifulSoup as soup

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.selenium_scraper import Selenium_Scraper


class Game_Prop_Scraper:
    def __init__(self, league, link):
        self.league = league
        self.link = link

    def create_df(self):
        cols = ["datetime", "Home", "Away", "Title", "Team/Player", "Odds", "scraped_ts"]
        return pd.DataFrame(columns=cols)

    def find_headers(self, sp):  # Top Level
        """
        finds all the available headers to click on to get different
        types of prop bets
        - separates out long string when a lowercase letter meets an uppercase
        """
        # s = Selenium_Scraper(self.link, [])
        full_str = sp.find_all('ul', attrs={'class': 'collectionList'})
        full_str = full_str[0].get_text()

        headers = []
        last_break = 0
        for i, char in enumerate(full_str):
            if i == 0:
                continue

            if (full_str[i].isupper()) and (full_str[i - 1].islower()):
                new_header = full_str[last_break:i]
                headers.append(new_header)
                last_break = i
        return headers

    def get_market_cards(self, sp, df):
        cards = sp.find_all('div', attrs={'class': 'MarketCard'})
        for card in cards:
            try:
                title = card.find_all('span', attrs={'class': 'title'})[0].get_text()
                print(title)
                bets = card.find_all('div', attrs={'class': 'outcomeTitle'})
                bets = [bet.get_text() for bet in bets]
                print(bets)
                odds = card.find_all('div', attrs={'class': 'outcomeOption'})
                odds = [item.get_text() for item in odds]
                odds = [item if item != "" else "NL" for item in odds]
                print(odds)
                for bet, odd in zip(bets, odds):
                    df.loc[len(df)] = ["datetime", "home", "away", title, bet, odd, "scraped"]
            except BaseException:
                print('error!')
        return df

    def navigate_to_section(self):  # Top Level
        pass

    def run(self):  # Run
        # get bets on current section
        # navigate to new section
        # repeat
        df = self.create_df()

        s = Selenium_Scraper(self.link, [])
        s.driver.get(s.start_link)
        time.sleep(8)
        start_sp = soup(s.driver.page_source, 'html.parser')

        sps = []
        elements = s.driver.find_elements_by_xpath("//li[@class='listButton collectionItem']")
        for element in elements:
            element.click()
            time.sleep(3)
            new_sp = soup(s.driver.page_source, 'html.parser')
            sps.append(new_sp)

        # try:
        #     while True:
        #         s.driver.find_element_by_xpath("//li[@class='listButton collectionItem']").click()
        #         time.sleep(3)
        # except BaseException:
        #     print('done')

        # headers = self.find_headers(start_sp)
        # print(headers)

        # sps = []
        # for header in headers[1:]:
        #     s.driver.find_element_by_xpath("//")
        #     link = s.driver.find_element_by_link_text(header)
        #     link.click()
        #     time.sleep(3)
        #     new_sp = soup(s.driver.page_source, 'html.parser')
        #     sps.append(new_sp)

        s.driver.close()


if __name__ == "__main__":
    link = 'https://www.williamhill.com/us/nj/bet/basketball/BE_EV1e72efd4-7ff7-4d2e-a93b-0d85de49e229/oklahoma-city-thunder-at-houston-rockets'
    # s = Selenium_Scraper(link, [])
    # sp = s.run()
    x = Game_Prop_Scraper("NBA", link)
    self = x
    # x.run()
