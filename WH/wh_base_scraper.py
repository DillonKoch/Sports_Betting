# ==============================================================================
# File: wh_base_scraper.py
# Project: Data
# File Created: Saturday, 29th August 2020 4:57:15 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 30th August 2020 9:11:18 am
# Modified By: Dillon Koch
# -----
#
# -----
# base scraper for all william hill sportsbook scrapers
# ==============================================================================


import abc
import sys
from os.path import abspath, dirname

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class WH_Base_Scraper(metaclass=abc.ABCMeta):
    def __init__(self, league, bet_name, sp=None):
        self.league = league
        self.bet_name = bet_name
        self.sp = sp
        self.df_path = ROOT_PATH + "/WH/Data/{}/{}.csv".format(self.league, self.bet_name)

    @abc.abstractmethod
    def update_df(self):
        """
        each sub-scraper must have an update_df method for wh_perform_scrapes.py
        """
        pass


if __name__ == "__main__":
    pass
