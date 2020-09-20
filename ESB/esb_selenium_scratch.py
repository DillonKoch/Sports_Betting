# ==============================================================================
# File: esb_selenium_scratch.py
# Project: Data
# File Created: Saturday, 12th September 2020 7:44:07 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 18th September 2020 8:05:32 pm
# Modified By: Dillon Koch
# -----
#
# -----
# temporarily trying to get sp in a much more efficient way
# ==============================================================================


import json
import sys
import time
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup
from selenium import webdriver

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESB_Selenium_Scraper:
    def __init__(self):
        self.start_link = 'https://www.elitesportsbook.com/sports/home.sbk'

    @property
    def config(self):  # Property
        with open(ROOT_PATH + "/ESB/config.json", 'r') as f:
            config = json.load(f)
        return config

    def _get_soup_sp(self):  # Global Helper
        """
        saves the selenium window's current page as a beautifulsoup object
        """
        html = self.driver.page_source
        sp = soup(html, 'html.parser')
        return sp

    def reset_window(self):  # Top Level
        """
        takes a selenium window to the Elite Sportsbook homepage
        """
        time.sleep(1)
        self.driver.get(self.start_link)
        welcome_clicks = self.config['Welcome Page Clicks']
        for button in welcome_clicks:
            time.sleep(5)
            link = self.driver.find_element_by_link_text(button)
            link.click()

    def get_section_pairs(self, homepage_sp):  # Top Level
        """
        Uses the homepage sp to find the relevant sections (main dropdowns on left side like NBA, NCAAF, etc)
        - returns a list of tuples [("NFL", <sp>), ("NBA", <sp>), (leauge, <sp>), ...]
        """
        relevant_section_names = list(self.config['Scrape Panels'].keys())
        sections = homepage_sp.find_all('div', attrs={'class': 'panel panel-primary'})

        section_pairs = []
        for section in sections:
            title = section.find_all('h4', attrs={'class': 'panel-title'})
            title = title[0].get_text().strip() if len(title) > 0 else None

            if title in relevant_section_names:
                league = self.config['Scrape Panels'][title]
                section_pairs.append((league, section))
        return section_pairs

    def find_nested_dropdowns(self, section, title):  # Top Level
        drops = section.find_all('a', attrs={'data-toggle': 'collapse'})
        drops = [item.get_text().strip() for item in drops]
        new_drops = [drop for drop in drops if drop not in title]
        return new_drops

    def get_section_title(self, sp):  # Top Level
        title = sp.find_all('h4', attrs={'class': 'panel-title'})[0]
        title = title.get_text().strip()
        return title

    def click_section(self, title):  # Top Level
        time.sleep(2)
        button = self.driver.find_element_by_link_text(title.upper())
        button.click()

    def click_nested_dropdowns(self, nested_dropdowns):  # Top Level
        # self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        # fails = 0
        # while fails < 2:
        #     try:
        for nd in nested_dropdowns:
            time.sleep(3)
            button = self.driver.find_element_by_link_text(nd)
            button.click()
            # except BaseException:
            #     print('FAIL')
            #     fails += 1

    def get_events(self, sp):  # Top Level
        events = sp.find_all('a', attrs={'class': 'ev'})
        events = [item.get_text().strip() for item in events]
        return events

    def click_event(self, event):  # Top Level
        button = self.driver.find_element_by_link_text(event)
        button.click()
        time.sleep(3)

    def run(self):  # Run
        self.driver = webdriver.Firefox(executable_path=r'/home/allison/Documents/geckodriver')
        self.reset_window()
        homepage_sp = self._get_soup_sp()

        section_pairs = self.get_section_pairs(homepage_sp)
        for section_pair in section_pairs:
            league, sp = section_pair
            title = self.get_section_title(sp)
            self.click_section(title)
            nested_dropdowns = self.find_nested_dropdowns(sp, title)
            self.click_nested_dropdowns(nested_dropdowns)

            events = self.get_events(sp)
            for event in events:
                self.click_event(event)
                event_sp = self._get_soup_sp()
                # self.scraper.run(league, event_sp)
                print('running scraper for league {}'.format(league))

        time.sleep(5)
        self.driver.close()


if __name__ == '__main__':
    x = ESB_Selenium_Scraper()
    self = x
    # x.run()
