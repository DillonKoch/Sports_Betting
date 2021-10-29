# ==============================================================================
# File: db_injuries.py
# Project: allison
# File Created: Thursday, 28th October 2021 9:52:05 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 28th October 2021 9:52:05 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraping donbest.com for injury data
# ==============================================================================

import sys
import time
import urllib.request
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class DB_Injuries:
    def __init__(self, league):
        self.leauge = league
        # self.link = f"https://www.donbest.com/{self.leauge.lower()}/injuries"
        # ! changing to COVERS website
        self.link = f"https://www.covers.com/sport/basketball/ncaab/injuries"

    def _get_soup_sp(self):  # Global Helper
        """
        saves the selenium window's current page as a beautifulsoup object
        """
        html = self.driver.page_source
        sp = soup(html, 'html.parser')
        return sp

    def get_sp1(self, link):  # Top Level
        """
        scraping HTML from a link
        """
        user_agent = 'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.7) Gecko/2009021910 Firefox/3.0.7'
        headers = {'User-Agent': user_agent, }
        request = urllib.request.Request(link, None, headers)  # The assembled request
        response = urllib.request.urlopen(request)
        a = response.read().decode('utf-8', 'ignore')
        sp = soup(a, 'html.parser')
        return sp

    def start_selenium(self):  # Top Level
        """
        fires up the selenium window to start scraping
        """
        options = Options()
        # options.headless = True
        self.driver = webdriver.Firefox(executable_path=ROOT_PATH + "/Scrapers/geckodriver", options=options)
        time.sleep(1)

    def run(self):  # Run
        pass
        # self.start_selenium()
        # self.driver.get(self.link)
        # time.sleep(5)
        # sp = self._get_soup_sp()
        # # sp = self.get_sp1(self.link)
        # injury_holders = sp.find_all('div', attrs={'class': 'injuries-holder'})
        # print('here')


if __name__ == '__main__':
    league = "NFL"
    x = DB_Injuries(league)
    self = x
    # x.run()
