# ==============================================================================
# File: esb_parser.py
# Project: ESB
# File Created: Sunday, 16th May 2021 8:51:45 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 16th May 2021 8:51:46 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Elite Sportsbook parser -> saves data to ... TODO
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from scrapers.parent_parser import Parent_Parser


class ESB_Parser(Parent_Parser):
    def __init__(self):
        pass

    def detect_bet_type(self):  # Top Level
        """
        detects whether the bet is (1) Game Lines, (2) Game Props, or (3) Futures
        """
        pass

    def scrape_game_lines(self):  # Top Level
        df = self.game_lines_df()

    def scrape_game_props(self):  # Top Level
        df = self.game_props_df()

    def scrape_futures(self):  # Top Level
        df = self.futures_df()

    def run(self, html, league):  # Run
        # determine bet type
        # scrape data to df
        # save data, merging with existing df
        bet_type = self.detect_bet_type(html)


if __name__ == '__main__':
    x = ESB_Parser()
    self = x
    x.run()
