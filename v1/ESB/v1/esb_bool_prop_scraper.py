# ==============================================================================
# File: esb_bool_prop_scraper.py
# Project: ESB
# File Created: Sunday, 23rd August 2020 10:07:20 am
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 23rd August 2020 10:12:35 am
# Modified By: Dillon Koch
# -----
#
# -----
# Boolean prop scraper for Elite Sportsbook
# ==============================================================================

"""
AT THE TIME OF REFACTORING THIS, THERE WERE NO BOOLEAN PROP BETS TO SCRAPE
- CONSULT ESB_PROP_SCRAPERS.PY FOR THE OLD CODE TO REFACTOR/ADD HERE
"""


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from ESB.esb_base_scraper import ESB_Base_Scraper


class ESB_Bool_Prop_Scraper(ESB_Base_Scraper):
    def __init__(self, league, bet_name, sp):
        super().__init__(league, bet_name, sp)

    def update_df(self):  # Run
        pass


if __name__ == "__main__":
    x = ESB_Bool_Prop_Scraper("NFL", "", None)
    self = x
