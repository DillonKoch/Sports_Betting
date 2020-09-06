# ==============================================================================
# File: wh_futures_scraper.py
# Project: WH
# File Created: Friday, 4th September 2020 5:59:38 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 4th September 2020 6:04:28 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraping futures bets from william hill sportsbook
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class WH_Futures_Scraper:
    def __init__(self):
        pass

    def run(self):  # Run
        pass


if __name__ == '__main__':
    x = WH_Futures_Scraper
    self = x
    x.run()
