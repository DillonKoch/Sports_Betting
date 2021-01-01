# ==============================================================================
# File: pb_navigator.py
# Project: PB
# File Created: Thursday, 31st December 2020 6:59:46 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 1st January 2021 12:14:57 am
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Navigator for PointsBet Sportsbook - https://ia.pointsbet.com/
# ==============================================================================

import re
import sys
import time
from os.path import abspath, dirname

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from ESB.esb_navigator import ESB_Navigator


class PB_Navigator(ESB_Navigator):
    def __init__(self):
        self.start_link = 'https://ia.pointsbet.com/'

    def reset_window(self, new_window=True):  # Top Level
        """
        takes a selenium window from any point to the PointsBet Sportsbook homepage
        """
        if new_window:
            self.driver = webdriver.Firefox(executable_path=ROOT_PATH + "/geckodriver")

        time.sleep(1)
        self.driver.get(self.start_link)
        homepage_sp = self._get_soup_sp()
        return homepage_sp

    def click_sidebar(self):  # Top Level
        """
        clicks the sidebar in the top left corner to locate "football" and "basketball" pages
        - selenium tutorial: https://www.youtube.com/watch?v=U6gbGk5WPws&t=302s
        - xpath info: https://selenium-python.readthedocs.io/locating-elements.html
        """
        _ = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH,
                                                                                "//button[@class='fd20fur']")))
        time.sleep(2)
        link = self.driver.find_element_by_xpath("//button[@class='fd20fur']")
        link.click()

    def sidebar_click_sport(self, sport: str):  # Top Level
        """
        once the sidebar is opened, this will click on a sport to view its page
        - football and basketball are the two I'm using to start with
        """
        assert sport in ['Football', 'Basketball'], "Invalid sport name!"
        _ = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located(
            (By.XPATH, "//a[@class='f10d1jnj f73eam3 f19szdeu f4ru8xs fztnm47 fsw11lo']")))
        link = self.driver.find_element_by_link_text(sport)
        link.click()
        time.sleep(2)

    def find_bet_sps(self, main_page_sp):  # Top Level
        """
        finds the sp for each individual bet shown on the sport's main page
        """
        bet_area_sp = sp.find_all('div', attrs={'class': 'facf5sk'})[0]
        bet_sps = bet_area_sp.find_all('div', attrs={'class': 'f17eajb7'})
        return bet_sps

    def expand_bets(self, main_page_sp):  # Top Level
        """
        expands the page to show all bet options (if some are covered in a dropdown)
        """
        dropdown_sp = main_page_sp.find_all('div', attrs={'class': 'f96or0t f10uq7qa fu0l42q'})
        for i in range(len(dropdown_sp)):
            link = self.driver.find_element_by_xpath("//button[@class='fq7xcxd']")
            link.click()
            time.sleep(2)

    def _multiple_extra_bets(self, link_sp):  # Specific Helper find_extra_bet_link
        """
        uses extra bets link sp to check if there are any extra wagers or not, so I can
        visit the link and scrape the extras if there are any
        - if there are extra wagers, the text will have "Wagers" instead of "Wager"
        - returns True if there are extra wagers, else False
        """
        link_sp_text = link_sp.get_text()
        multiple_bets_comp = re.compile(r"^.+Wagers$")
        multiple_bets = True if re.match(link_sp_text) else False
        # TODO pick up here

    def find_extra_bet_link(self, bet_sp):  # Top Level
        """
        for each bet, this finds the link that says "25 wagers" so I can go to all
        those sites later and get the more specific bets
        """
        link_sp = bet_sp.find_all('a', attrs={'class': 'f1x4xdln f1i1gs4f fsw11lo'})[0]
        if self._multiple_extra_bets(link_sp):
            link_extension = link_sp.get('href')
            full_link = self.base_link + link_extension
            return full_link.replace('//', '/')
        return None

    def run(self):  # Run
        new_window = True
        for sport in ['Football', 'Basketball'][:4]:
            self.reset_window(new_window)
            new_window = False
            self.click_sidebar()
            self.sidebar_click_sport(sport)
            main_page_sp = self._get_soup_sp()
            self.expand_bets(main_page_sp)

            bet_sps = self.find_bet_sps(main_page_sp)
            extra_bet_links = []
            for bet_sp in bet_sps:
                extra_bet_links += self.find_extra_bet_link(bet_sp)

        return extra_bet_links


if __name__ == '__main__':
    x = PB_Navigator()
    self = x
    sp = x.run()
