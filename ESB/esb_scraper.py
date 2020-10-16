# ==============================================================================
# File: esb_scraper.py
# Project: ESB
# File Created: Thursday, 15th October 2020 7:29:18 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 15th October 2020 8:09:28 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Elite Sportsbook web scraper
# ==============================================================================

# load the main page
# find the dropdown bars
# click each dropdown
# click each subdropdown
# grab sp for each page that has bets of interest
# pass that sp and info on the section/subsection to a parser
# parser gets all the data and updates df's
# run the data QA test


import json
import sys
import time
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESB_Scraper:
    def __init__(self):
        self.start_link = 'https://www.elitesportsbook.com/sports/home.sbk'

    @property
    def config(self):  # Property
        with open(ROOT_PATH + "/ESB/config.json", 'r') as f:
            config = json.load(f)
        return config

    def reset_window(self):  # Top Level
        """
        takes a selenium window from any point to the Elite Sportsbook homepage
        """
        time.sleep(1)
        self.driver.get(self.start_link)

        # click Iowa button
        _ = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "venueIowa")))
        link = self.driver.find_element_by_link_text("IOWA")
        link.click()

        # click BET NOW button
        _ = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located(
            (By.XPATH, "//a[@class='btn btn-primary px-5 py-3 mt-3 mr-2']")))
        time.sleep(2)
        link = self.driver.find_element_by_link_text("BET NOW")
        link.click()

    def run(self):  # Run
        self.driver = webdriver.Firefox(executable_path=r'/home/allison/Documents/geckodriver')
        self.reset_window()


if __name__ == '__main__':
    x = ESB_Scraper()
    self = x
    x.run()
