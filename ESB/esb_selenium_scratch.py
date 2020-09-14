# ==============================================================================
# File: esb_selenium_scratch.py
# Project: Data
# File Created: Saturday, 12th September 2020 7:44:07 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 12th September 2020 8:02:32 pm
# Modified By: Dillon Koch
# -----
#
# -----
# temporarily trying to get sp in a much more efficient way
# ==============================================================================


import sys
import time
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.selenium_scraper import Selenium_Scraper
from Utility.Utility import get_sp1


class ESB_Selenium_Scraper:
    def __init__(self):
        pass

    def run(self):  # Run
        link = 'https://www.elitesportsbook.com/sports/home.sbk'
        links_to_click = ['IOWA', 'BET NOW']
        s = Selenium_Scraper(link, links_to_click)
        s.run(close=False)
        sp = s.driver.page_source
        sp = soup(sp, 'html.parser')

        s.driver.get(link)
        time.sleep(10)

        accordion = sp.find_all('div', attrs={'id': 'accordion'})
        top_accordions = accordion[0].find_all('a', attrs={'class': 'topAccordion'})
        for ta in top_accordions:
            print(ta.get_text())


if __name__ == '__main__':
    x = ESB_Selenium_Scraper()
    self = x
    x.run()
