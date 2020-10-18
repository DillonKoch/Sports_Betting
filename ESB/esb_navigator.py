# ==============================================================================
# File: esb_navigator.py
# Project: ESB
# File Created: Thursday, 15th October 2020 7:29:18 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 17th October 2020 9:41:46 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Elite Sportsbook web scraper
# ==============================================================================


import datetime
import logging
import sys
import time
from os.path import abspath, dirname

from bs4 import BeautifulSoup as soup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESB.esb_parser import ESB_Parser


class ESB_Navigator:
    def __init__(self):
        self.start_link = 'https://www.elitesportsbook.com/sports/home.sbk'
        self.fake_nested_dropdowns = ['Iowa Season Long']

        # logger = logging.getLogger(__name__)
        # logger.setLevel(logging.INFO)
        today = datetime.date.today()
        year, month, day = today.year, today.month, today.day

        # handler = TimedRotatingFileHandler(f'ESB_Navigator_{year}_{month}_{day}.log', when='D', interval=7, backupCount=10)
        # formatter = logging.Formatter("%(asctime)s:%(levelname)s:%(message)s")
        # handler.setFormatter(formatter)
        # logger.addHandler(handler)
        logging.basicConfig(filename=f'./Logs/ESB_Navigator_{year}_{month}_{day}.log', level=logging.INFO,
                            format="%(asctime)s:%(levelname)s:%(message)s")
        self.logger = logging.getLogger(__name__)
        self.logger.info("Logger has been set up")

    @property
    def section_dict(self):  # Property
        """
        This dict includes the sections on the left side of the ESB homepage
        as keys, with the values being the league the section belongs to
        # ! May need to be updated if the site changes sections !
        """
        return {"Pro Football Game Lines": "NFL",
                "Pro Football Futures": "NFL",
                "NCAA FOOTBALL": "NCAAF",
                "NBA": "NBA",
                "NCAA Men's Basketball": "NCAAB"}

    def _get_soup_sp(self):  # Global Helper
        """
        saves the selenium window's current page as a beautifulsoup object
        """
        html = self.driver.page_source
        sp = soup(html, 'html.parser')
        return sp

    def reset_window(self, new_window=True):  # Top Level  Tested
        """
        takes a selenium window from any point to the Elite Sportsbook homepage
        """
        if new_window:
            self.driver = webdriver.Firefox(executable_path=ROOT_PATH + "/geckodriver")

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

        homepage_sp = self._get_soup_sp()
        self.logger.info("homepage sp found successfully")
        return homepage_sp

    def get_section_pairs(self, homepage_sp):  # Top Level
        """
        Uses the homepage sp to find the relevant sections (main dropdowns on left side like NBA, NCAAF, etc)
        - returns a list of tuples [("NFL", <sp>), ("NBA", <sp>), (leauge, <sp>), ...]
        """
        section_names = list(self.section_dict.keys())
        found_sections = homepage_sp.find_all('div', attrs={'class': 'panel panel-primary'})

        section_pairs = []
        for section in found_sections:
            title = section.find_all('h4', attrs={'class': 'panel-title'})
            title = title[0].get_text().strip() if len(title) > 0 else None

            if title in section_names:
                league = self.section_dict[title]
                section_pairs.append((league, section))
                self.logger.info(f"Found section pair for league '{league}', sp length: {len(str(section))}")
        return section_pairs

    def get_section_title(self, sp):  # Top Level
        """
        finds the section title given a section sp
        - e.g. "Pro Football Game Lines", "NCAA Basketball", ...
        """
        title = sp.find_all('h4', attrs={'class': 'panel-title'})[0]
        title = title.get_text().strip()
        self.logger.info(f"Found title {title}" + ("-" * 50))
        return title

    def click_button(self, name, upper=False):  # Top Level
        """
        clicks the button with text matching the 'name' argument
        """
        if upper:
            name = name.upper()
        time.sleep(5)
        button = self.driver.find_element_by_link_text(name)
        button.click()
        self.logger.info(f"Clicked button {name}")

    def find_nested_dropdowns(self, section, title):  # Top Level
        """
        finds the names of nested dropdown buttons under the main section title
        - these need to be clicked too to find all the events under them
        """
        drops = section.find_all('a', attrs={'data-toggle': 'collapse'})
        drops = [item.get_text().strip() for item in drops]
        new_drops = [drop for drop in drops if drop not in title]
        for drop in new_drops:
            self.logger.info(f"Found nested dropdown {drop}")
        return new_drops

    def click_nested_dropdowns(self, nested_dropdowns):  # Top Level
        """
        clicks all the nested dropdowns to show all the section's events
        - some nested dropdowns are actually bets themselves (Iowa Season long is one example),
          so this function also returns those page sp's if the nd name is in self.fake_nested_dropdowns
        """
        fake_sps = []
        for nd in nested_dropdowns:
            self.click_button(nd)

            if nd in self.fake_nested_dropdowns:
                fake_sp = self._get_soup_sp()
                fake_sps.append(fake_sp)
            self.logger.info(f"Clicked nested dropdown {nd}")
        return fake_sps

    def get_events(self, sp):  # Top Level
        """
        finds the text of all the events currently shown
        """
        events = sp.find_all('a', attrs={'class': 'ev'})
        events = [item.get_text().strip() for item in events]
        for event in events:
            self.logger.info(f"Found event {event}")
        return events

    def run(self):  # Run
        homepage_sp = self.reset_window()
        section_pairs = self.get_section_pairs(homepage_sp)
        sps = []
        for section_pair in section_pairs:
            league, sp = section_pair
            parser = ESB_Parser(league)
            title = self.get_section_title(sp)
            self.click_button(title, upper=True)
            nested_dropdowns = self.find_nested_dropdowns(sp, title)
            fake_dropdowns = self.click_nested_dropdowns(nested_dropdowns)

            events = self.get_events(sp)
            all_events = events + fake_dropdowns
            for event in all_events:
                self.click_button(event)
                event_sp = self._get_soup_sp()
                parser_msg = parser.run(event_sp)  # TODO have the parser return a msg to put in log file
                self.logger.info("<<parser message here>>")
                sps.append((league, event_sp))

        time.sleep(5)
        self.driver.close()

        self.driver.quit()
        return sps


if __name__ == '__main__':
    x = ESB_Navigator()
    self = x
    sps = x.run()
