# ==============================================================================
# File: esb_selenium_scratch.py
# Project: Data
# File Created: Saturday, 12th September 2020 7:44:07 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 22nd September 2020 4:37:47 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Searching for HTML using one selenium window instead of one per bet
# then pulling in the ESB general scraper to actually scrape and udpate df's
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

from ESB.esb_general_scraper import ESB_General_Scraper


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
            time.sleep(15)
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

    def get_section_title(self, sp):  # Top Level
        """
        finds the section title given a section sp
        - e.g. "Pro Football Game Lines", "NCAA Basketball", ...
        """
        title = sp.find_all('h4', attrs={'class': 'panel-title'})[0]
        title = title.get_text().strip()
        return title

    def click_button(self, name, upper=False):  # Top Level
        """
        clicks the button with text matching the 'title' argument
        """
        if upper:
            name = name.upper()
        time.sleep(5)
        button = self.driver.find_element_by_link_text(name)
        button.click()

    def find_nested_dropdowns(self, section, title):  # Top Level
        """
        finds the names of nested dropdown buttons under the main section title
        - these need to be clicked too to find all the events under them
        """
        drops = section.find_all('a', attrs={'data-toggle': 'collapse'})
        drops = [item.get_text().strip() for item in drops]
        new_drops = [drop for drop in drops if drop not in title]
        return new_drops

    def click_nested_dropdowns(self, nested_dropdowns):  # Top Level
        """
        clicks all the nested dropdowns to show all the section's events
        """
        for nd in nested_dropdowns:
            self.click_button(nd)
        # for nd in nested_dropdowns:
        #     time.sleep(3)
        #     button = self.driver.find_element_by_link_text(nd)
        #     button.click()

    def get_events(self, sp):  # Top Level
        """
        finds the text of all the events currently shown
        """
        events = sp.find_all('a', attrs={'class': 'ev'})
        events = [item.get_text().strip() for item in events]
        return events

    def run(self):  # Run
        self.driver = webdriver.Firefox(executable_path=r'/home/allison/Documents/geckodriver')
        self.reset_window()
        homepage_sp = self._get_soup_sp()

        section_pairs = self.get_section_pairs(homepage_sp)
        for section_pair in section_pairs:
            league, sp = section_pair
            scraper = ESB_General_Scraper(league)
            title = self.get_section_title(sp)
            self.click_button(title, upper=True)
            nested_dropdowns = self.find_nested_dropdowns(sp, title)
            self.click_nested_dropdowns(nested_dropdowns)

            events = self.get_events(sp)
            for event in events:
                self.click_button(event)
                event_sp = self._get_soup_sp()
                scraper.run(event_sp)

        time.sleep(5)
        self.driver.close()


if __name__ == '__main__':
    x = ESB_Selenium_Scraper()
    self = x
    x.run()
