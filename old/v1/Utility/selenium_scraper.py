# ==============================================================================
# File: selenium_scraper.py
# Project: Utility
# File Created: Wednesday, 5th August 2020 11:41:28 am
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 12th September 2020 7:55:39 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Using selenium to click through a path of links to a certain webpage
# ==============================================================================


import sys
import time
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup
from selenium import webdriver

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Selenium_Scraper:
    def __init__(self, start_link, links_to_click):
        # self.start_link = "https://www.elitesportsbook.com/sports/home.sbk"
        self.start_link = start_link
        self.links_to_click = links_to_click
        self.driver = webdriver.Firefox(executable_path=r'/home/allison/Documents/geckodriver')

    def run(self, close=True):  # Run
        """
        starts at the start_link, then clicks through the path given and returns
        the sp of the final destination
        """
        self.driver.get(self.start_link)
        # wait for the redirect to happen
        for i in range(10):
            print(i)
            time.sleep(1)

        # click through the path
        for link in self.links_to_click:
            print(link)
            link = self.driver.find_element_by_link_text(link)
            link.click()
            time.sleep(5)

        html = self.driver.page_source
        sp = soup(html, 'html.parser')
        if close:
            self.driver.close()
        return sp


if __name__ == "__main__":
    links_to_click = ["IOWA", 'BET NOW']  # , 'NBA', "Game Lines", "Full Game"]
    x = Selenium_Scraper("https://www.elitesportsbook.com/sports/home.sbk", links_to_click)
    sp = x.run()
