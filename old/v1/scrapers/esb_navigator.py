# ==============================================================================
# File: esb_navigator.py
# Project: ESB
# File Created: Sunday, 16th May 2021 5:53:39 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 16th May 2021 5:53:40 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Elite Sportsbook navigator
# ==============================================================================


import pickle
import sys
from os.path import abspath, dirname

from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from scrapers.esb_parser import ESB_Parser
from scrapers.parent_navigator import Parent_Navigator

sys.setrecursionlimit(1000000000)

# TODO create decorator that tells me where errors come up for each method
# TODO some sort of monitoring that tells me how this stuff is going, if there are errors
# TODO look up some cool selenium tricks I probably don't know atm


class ESB_Navigator(Parent_Navigator):
    def __init__(self):
        self.esb_link = "https://www.elitesportsbook.com/sports/home.sbk"
        self.parser = ESB_Parser()
        self.sidebar_dict = {"Pro Football Game Lines": "NFL",
                             "Pro Football Futures": "NFL",
                             "NCAA FOOTBALL": "NCAAF",
                             "NBA": "NBA",
                             "NCAA Men's Basketball": "NCAAB"}
        self.leagues = list(self.sidebar_dict.keys())

    def click_Iowa_button(self):  # Top Level
        """
        clicks on the "IOWA" button to take the driver to the homepage
        """
        _ = WebDriverWait(self.driver, 20).until(EC.presence_of_element_located((By.ID, "venueIowa")))
        link = self.driver.find_element_by_link_text("IOWA")
        link.click()
        return self.get_html()

    def _sidebar_title(self, sidebar_html):  # Specific Helper get_sidebar_htmls, sidebar_info
        """
        returns the title of a sidebar_html
        """
        return sidebar_html.find_all('h4', attrs={'class': 'panel-title'})[0].get_text().strip()

    def get_sidebar_htmls(self, homepage_html):  # Top Level
        """
        returns the html for all the sports sidebars
        """
        full_sidebar_html = homepage_html.find_all('div', attrs={'id': 'accordion'})[0]
        sidebar_htmls = full_sidebar_html.find_all('div', attrs={'class': 'panel panel-primary'})
        sidebar_htmls = [sh for sh in sidebar_htmls if self._sidebar_title(sh) in self.leagues]
        return sidebar_htmls

    def _sidebar_nested_dropdowns(self, sidebar_html):  # Specific Helper  sidebar_info
        """
        returns the titles of the nested dropdowns in a sidebar_html (nd = nested_dropdown)
        """
        nd_html = sidebar_html.find_all('tr')
        # nds = [nd.find_all('a', attrs={'data-toggle': 'collapse'})[0].get_text().strip() for nd in nd_html]
        nds = [nd.find_all('a', attrs={'data-toggle': 'collapse'}) for nd in nd_html]
        nds = [nd[0].get_text().strip() for nd in nds if len(nd) > 0]
        return nds

    def _sidebar_bets(self, sidebar_html):  # Specific Helper sidebar_info
        """
        returns the names of the bets in a sidebar_html
        """
        bet_htmls = sidebar_html.find_all('a', attrs={'class': 'ev'})
        bets = [bh.get_text().strip() for bh in bet_htmls]
        return bets

    def sidebar_info(self, sidebar_html):  # Top Level
        """
        parses data from the sidebar html: (title, nested_dropdowns, bets)
        """
        title = self._sidebar_title(sidebar_html)
        nested_dropdowns = self._sidebar_nested_dropdowns(sidebar_html)
        bets = self._sidebar_bets(sidebar_html)
        return title, nested_dropdowns, bets

    def save_pickle(self, bet_html, league, i):  # Top Level
        """
        saves the necessary data for the parser to run tests to /test/data/esb/
        """
        pickle_obj = [bet_html, league]
        path = ROOT_PATH + f"/test/data/esb/{league}_{i}.pickle"
        with open(path, 'wb') as f:
            pickle.dump(pickle_obj, f)

    def run(self):  # Run
        self.new_window(self.esb_link)
        homepage_html = self.click_Iowa_button()

        sidebar_htmls = self.get_sidebar_htmls(homepage_html)
        for sidebar_html in sidebar_htmls:
            title, nested_dropdowns, bets = self.sidebar_info(sidebar_html)
            self.click_button(title.upper())

            for nested_dropdown in nested_dropdowns:
                self.click_button(nested_dropdown)

            for i, bet in enumerate(bets):
                bet_html = self.click_button(bet)
                self.parser.run(bet_html, self.sidebar_dict[title])
                self.save_pickle(bet_html, self.sidebar_dict[title], i)

        self.exit_browser()


if __name__ == '__main__':
    x = ESB_Navigator()
    self = x
    x.run()
