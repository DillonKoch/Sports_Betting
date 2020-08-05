# ==============================================================================
# File: esb_perform_scrapes.py
# Project: ESB_Scrapers
# File Created: Tuesday, 23rd June 2020 3:20:11 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 5th August 2020 3:26:04 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for performing all ESB Scraping in one place regardless of bet type (prop, bool prop, game)
# ==============================================================================

import json
import sys
import time
from os.path import abspath, dirname


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESB_Scrapers.esb_game_scraper import ESB_Game_Scraper
from ESB_Scrapers.esb_prop_scrapers import (ESB_Bool_Prop_Scraper,
                                            ESB_Prop_Scraper)
from ESB_Scrapers.esb_selenium import ESB_Selenium
from Utility.Utility import get_sp1, parse_league


class ESB_Perform_Scrapes:
    def __init__(self, league):
        self.league = league

    @property
    def config(self):  # Property
        with open("{}_esb.json".format(self.league.lower())) as f:
            config = json.load(f)
        return config

    @property
    def scraper_dict(self):  # Property
        scraper_dict = {
            "Games": ESB_Game_Scraper,
            "Prop": ESB_Prop_Scraper,
            "Bool_Prop": ESB_Bool_Prop_Scraper
        }
        return scraper_dict

    def scrape_bet(self, sp, bet_name, bet_type):  # Top Level
        scrape_func = self.scraper_dict[bet_type]
        esb_scraper = scrape_func(self.league, bet_name, sp)
        esb_scraper.update_df()
        print("{} updated".format(bet_name))

    def _selenium_get_sp(self, links_to_click):  # Specific Helper scrape_sp
        s = ESB_Selenium(links_to_click)
        sp = s.run()
        return sp

    def scrape_sp(self, link, links_to_click):  # Top Level
        try:
            sp = get_sp1(link)
            if len(str(sp)) == 23393:
                raise ValueError("Redirected")
        except Exception as e:
            print(e)
            print("ERROR SCRAPING WITH BEAUTIFULSOUP - TRYING WITH SELENIUM")
            sp = self._selenium_get_sp(links_to_click)
        return sp

    def run(self):  # Run
        for bet in self.config["Bets"]:
            bet_name, link, bet_type, links_to_click = bet
            print("Updating {}...".format(bet_name))
            try:
                print('here')
                sp = self.scrape_sp(link, links_to_click)
                # sp = get_sp1(link)
                self.scrape_bet(sp, bet_name, bet_type)
            except Exception as e:
                print("-" * 30)
                print(f"ERROR UPDATING BET {bet_name}! ({e})")
                print("-" * 30)
            time.sleep(5)


if __name__ == "__main__":
    league = parse_league()
    # league = "NFL"
    x = ESB_Perform_Scrapes(league)
    x.run()
