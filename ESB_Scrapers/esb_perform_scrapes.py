# ==============================================================================
# File: esb_perform_scrapes.py
# Project: ESB_Scrapers
# File Created: Tuesday, 23rd June 2020 3:20:11 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 23rd June 2020 3:21:52 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for performing all ESB Scraping in one place regardless of bet type (prop, bool prop, game)
# ==============================================================================

import json
import os
import sys
from os.path import abspath, dirname

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.Utility import get_sp1


class ESB_Perform_Scrapes:
    @property
    def config(self):  # Property
        with open("{}_esb.json".format(self.league.lower())) as f:
            config = json.load(f)
        return config

    def run_all_updates(self):  # Run
        bet_lists = self.config["Bets"]
        for bet_list in bet_lists:
            bet_name, link, category = bet_list
            sp = get_sp1(link)

            if self._bet_df_exists(bet_name):
                self.update_bet_df(bet_name, category, sp)
            else:
                self.make_new_df(bet_name, category, sp)
        print("DONE")

    def update_bet_df(self, bet_name, category, sp):  # Run
        full_path = ROOT_PATH + "/ESB_Data/{}/{}.csv".format(self.league, bet_name)
        existing_df = pd.read_csv(full_path)

        if category == "Games":
            new_df = self._update_games_df(sp)
        elif category == "Prop":
            new_df = self._update_prop_df(sp)
        elif category == "Bool_Prop":
            new_df = self._update_bool_prop_df(sp)

        new_df = self._update_games_df(existing_df, sp) if category == "Games" else self._update_prop_df(existing_df, sp)
        new_df.to_csv(full_path)

    def _bet_df_exists(self, bet_list):  # Specific Helper run_all_updates
        bet_list_title, link, category = bet_list
        df_name = bet_list_title + ".csv"
        return True if df_name in os.listdir(ROOT_PATH + "/ESB_Data/{}/".format(self.league)) else False
