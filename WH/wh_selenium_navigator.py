# ==============================================================================
# File: wh_selenium_navigator.py
# Project: WH
# File Created: Tuesday, 22nd September 2020 8:15:40 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 22nd September 2020 8:28:38 pm
# Modified By: Dillon Koch
# -----
#
# -----
# William Hill Selenium Navigator to find all the sp for bets
# ==============================================================================


import sys
import time
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup
from selenium import webdriver

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class WH_Selenium_Navigator:
    def __init__(self):
        self.start_link = "https://www.williamhill.com/us/nj/bet/"

    def _get_soup_sp(self):  # Global Helper
        """
        saves the selenium window's current page as a beautifulsoup object
        """
        html = self.driver.page_source
        sp = soup(html, 'html.parser')
        return sp

    def reset_window(self):  # Top Level
        """
        takes a selenium window to the William Hill Sportsbook homepage
        """
        time.sleep(2)
        self.driver.get(self.start_link)
        time.sleep(2)

    def run(self):  # Run
        self.driver = webdriver.Firefox(executable_path=r'/home/allison/Documents/geckodriver')

        homepage_sp = self._get_soup_sp()
        sidebars = homepage_sp.find_all('div', attrs={'class': 'sideNavigation'})


if __name__ == '__main__':
    x = WH_Selenium_Navigator()
    self = x
    x.run()
