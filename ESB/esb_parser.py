# ==============================================================================
# File: esb_parser.py
# Project: ESB
# File Created: Saturday, 17th October 2020 8:05:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 17th October 2020 9:31:54 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Elite Sportsbook BeautifulSoup parser
# * BeautifulSoup sp is found in esb_navigator.py, passed to this class for parsing
# ==============================================================================

import datetime
import sys
from os.path import abspath, dirname

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESB_Parser:
    def __init__(self, league):
        self.league = league

    def _get_scrape_ts(self):  # Global Helper  Tested
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M")

    def run(self, sp):  # Run
        pass


if __name__ == '__main__':
    x = ESB_Parser()
    self = x
    x.run()
