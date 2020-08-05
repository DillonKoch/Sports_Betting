# ==============================================================================
# File: ESB_Seleniumer.py
# Project: ESB_Scrapers
# File Created: Wednesday, 5th August 2020 11:41:28 am
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 5th August 2020 2:46:29 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Using selenium to avoid the initial page you have to click through
# ==============================================================================


from os.path import abspath, dirname
import sys
import time
from bs4 import BeautifulSoup as soup

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from selenium import webdriver


class ESB_Selenium:
    def __init__(self, links_to_click):
        self.start_link = "https://www.elitesportsbook.com/sports/home.sbk"
        self.links_to_click = links_to_click
        self.driver = webdriver.Firefox(executable_path=r'/home/allison/Documents/geckodriver')

    def run(self):  # Run
        """
        starts at the ESB homepage, then clicks through the path given and returns html
        """
        self.driver.get(self.start_link)
        # wait for the redirect to happen
        for i in range(5):
            print(i)
            time.sleep(1)

        # click through the path
        for link in self.links_to_click:
            print(link)
            link = self.driver.find_element_by_link_text(link)
            link.click()
            time.sleep(1)

        html = self.driver.page_source
        sp = soup(html, 'html.parser')
        self.driver.close()
        return sp


if __name__ == "__main__":
    links_to_click = ['BET NOW', 'NBA', "Game Lines", "Full Game"]
    x = ESB_Selenium(links_to_click)
    sp = x.run()
