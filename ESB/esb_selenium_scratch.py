# ==============================================================================
# File: esb_selenium_scratch.py
# Project: Data
# File Created: Saturday, 12th September 2020 7:44:07 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 18th September 2020 2:32:21 pm
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
    def __init__(self, start_link):
        self.start_link = start_link

    @property
    def config(self):  # Property
        with open(ROOT_PATH + "/ESB/config.json", 'r') as f:
            config = json.load(f)
        return config

    def _get_soup_sp(self):  # Global Helper
        html = self.driver.page_source
        sp = soup(html, 'html.parser')
        return sp

    def reset_window(self):  # Top Level
        self.driver.get(self.start_link)
        welcome_clicks = self.config['Welcome Page Clicks']
        for button in welcome_clicks:
            time.sleep(4)
            link = self.driver.find_element_by_link_text(button)
            link.click()

    def find_league_dropdowns(self, sp):  # Top Level
        accordion = sp.find_all('div', attrs={'id': 'accordion'})
        panel_titles = accordion[0].find_all('h4', attrs={'class': 'panel-title'})
        panel_names = [panel.get_text().strip().upper() for panel in panel_titles]
        return panel_names

        # for name in panel_names:
        #     print(name)
        #     link = self.driver.find_element_by_link_text(name.upper())
        #     link.click()
        #     time.sleep(2)

    def run(self):  # Run
        self.driver = webdriver.Firefox(executable_path=r'/home/allison/Documents/geckodriver')
        time.sleep(2)
        self.reset_window()
        homepage_sp = self._get_soup_sp()
        panel_names = self.find_league_dropdowns(homepage_sp)

        for panel_name in panel_names[:1]:
            # click the panel
            link = self.driver.find_element_by_link_text(panel_name)
            link.click()
            time.sleep(3)

            panel_sp = self._get_soup_sp()
            accordion = panel_sp.find_all('div', attrs={'id': 'accordion'})
            # ncaaf = accordion[0].find_all('div', attrs={'class':'panel-body'})[2]

            # --------------
            # link = self.driver.find_element_by_link_text("Game Lines")
            # link.click()
            # print('here!')
            # --------------

            # click any sub-panels
            # click all the end bets
            # gather all the sp's of the end bets and scrape for bets, updating df's

        time.sleep(5)
        self.driver.close()

    def get_relevant_panels(self, homepage_sp):  # Top Level
        panels = homepage_sp.find_all('div', attrs={'class': 'panel panel-primary'})
        relevant_panels = []
        for panel in panels:
            title = panel.find_all('h4', attrs={'class': 'panel-title'})
            title = title[0].get_text().strip() if len(title) > 0 else None
            if title in self.config['Scrape Panels']:
                relevant_panels.append(panel)
        return relevant_panels

    def find_nested_dropdowns(self, panel, title):  # Top Level
        drops = panel.find_all('a', attrs={'data-toggle': 'collapse'})
        drops = [item.get_text().strip() for item in drops]
        new_drops = [drop for drop in drops if drop not in title]
        return new_drops

    def run(self):  # Run
        self.driver = webdriver.Firefox(executable_path=r'/home/allison/Documents/geckodriver')
        time.sleep(5)
        self.reset_window()
        homepage_sp = self._get_soup_sp()

        final_sps = []
        panels = self.get_relevant_panels(homepage_sp)
        for panel in panels:
            time.sleep(3)
            title = panel.find_all('h4', attrs={'class': 'panel-title'})[0].get_text().strip()
            print('title', title)
            button = self.driver.find_element_by_link_text(title.upper())
            button.click()
            time.sleep(3)

            nested_dropdowns = self.find_nested_dropdowns(panel, title)
            for nd in nested_dropdowns:
                button = self.driver.find_element_by_link_text(nd)
                button.click()
                time.sleep(3)

            events = panel.find_all('a', attrs={'class': 'ev'})
            events = [item.get_text().strip() for item in events]
            for event in events:
                button = self.driver.find_element_by_link_text(event)
                button.click()
                time.sleep(3)

                current_sp = self._get_soup_sp()
                final_sps.append((title, event, current_sp))

        time.sleep(5)
        self.driver.close()

    # def run(self):  # Run
    #     link = 'https://www.elitesportsbook.com/sports/home.sbk'
    #     links_to_click = ['IOWA', 'BET NOW']
    #     s = Selenium_Scraper(link, links_to_click)
    #     s.run(close=False)
    #     sp = s.driver.page_source
    #     sp = soup(sp, 'html.parser')

    #     s.driver.get(link)
    #     time.sleep(10)

    #     accordion = sp.find_all('div', attrs={'id': 'accordion'})
    #     top_accordions = accordion[0].find_all('a', attrs={'class': 'topAccordion'})
    #     for ta in top_accordions:
    #         print(ta.get_text())
if __name__ == '__main__':
    link = 'https://www.elitesportsbook.com/sports/home.sbk'
    x = ESB_Selenium_Scraper(link)
    self = x
    # x.run()
