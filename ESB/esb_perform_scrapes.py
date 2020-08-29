# ==============================================================================
# File: esb_perform_scrapes.py
# Project: ESB_Scrapers
# File Created: Tuesday, 23rd June 2020 3:20:11 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 29th August 2020 4:13:45 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for performing all ESB Scraping in one place regardless of bet type (prop, bool prop, game)
# ==============================================================================

import json
import pandas as pd
import sys
import time
import os
from os.path import abspath, dirname

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESB.esb_game_scraper import ESB_Game_Scraper
from ESB.esb_multiple_futures_scraper import ESB_Multiple_Futures_Scraper
from ESB.esb_bool_prop_scraper import ESB_Bool_Prop_Scraper
from ESB.esb_prop_scraper import ESB_Prop_Scraper
from Utility.selenium_scraper import Selenium_Scraper
from Utility.Utility import get_sp1, listdir_fullpath, parse_league
from Utility.sqlite_util import Sqlite_util


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
            "Bool_Prop": ESB_Bool_Prop_Scraper,
            "Multiple Futures": ESB_Multiple_Futures_Scraper
        }
        return scraper_dict

    def scrape_bet(self, sp, bet_name, bet_type):  # Top Level
        scrape_func = self.scraper_dict[bet_type]
        esb_scraper = scrape_func(self.league, bet_name, sp)
        esb_scraper.update_df()
        print("-" * 25 + "{} updated".format(bet_name) + "-" * 25)

    def _selenium_get_sp(self, links_to_click):  # Specific Helper scrape_sp
        s = Selenium_Scraper("https://www.elitesportsbook.com/sports/home.sbk", links_to_click)
        sp = s.run()
        return sp

    def scrape_sp(self, link, links_to_click):  # Top Level
        try:
            sp = get_sp1(link)
            print(len(str(sp)))
            if len(str(sp)) == 24115:
                raise ValueError("ERROR: Elite Sportsbook redirected to a welcome page")
        except Exception as e:
            print(e)
            print("ERROR SCRAPING WITH BEAUTIFULSOUP - TRYING WITH SELENIUM")
            sp = self._selenium_get_sp(links_to_click)
        return sp

    def add_to_database(self):  # Top Level
        s = Sqlite_util()
        bet_files = listdir_fullpath(ROOT_PATH + "/ESB/Data/{}/".format(self.league))
        for bet_file in bet_files:
            df = pd.read_csv(bet_file)

            table_name = bet_file.split("/")[-1].replace('.csv', '')
            table_name = "ESB_" + self.league + "_" + table_name
            s.insert_df(df, table_name)

    def run(self):  # Run
        for bet in self.config["Bets"]:
            bet_name, link, bet_type, links_to_click = bet
            print("Updating {}...".format(bet_name))
            try:
                sp = self.scrape_sp(link, links_to_click)
                self.scrape_bet(sp, bet_name, bet_type)
            except Exception as e:
                print("-" * 30)
                print(f"ERROR UPDATING BET {bet_name}! ({e})")
                print("-" * 30)
            time.sleep(5)
        self.add_to_database()


if __name__ == "__main__":
    league = parse_league()
    # league = "NFL"
    x = ESB_Perform_Scrapes(league)
    x.run()
