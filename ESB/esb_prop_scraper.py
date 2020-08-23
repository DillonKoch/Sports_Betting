# ==============================================================================
# File: esb_prop_scraper.py
# Project: ESB
# File Created: Sunday, 23rd August 2020 10:13:21 am
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 23rd August 2020 11:31:06 am
# Modified By: Dillon Koch
# -----
#
# -----
# scraper for prop bets on Elite Sportsbook
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESB.esb_base_scraper import ESB_Base_Scraper


class ESB_Prop_Scraper(ESB_Base_Scraper):

    def __init__(self, league, bet_name, sp):
        super().__init__(league, bet_name, sp)

    @property
    def df_cols(self):
        return ["Title", "description", "Team/Player", "Odds", "scraped_ts"]

    def _get_bets(self):  # Specific Helper make_new_df
        teams = self.sp.find_all('span', attrs={'class': 'team'})
        teams += self.sp.find_all('span', attrs={'class': 'team-title'})
        teams = [item.get_text() for item in teams]

        odds = self.sp.find_all('div', attrs={'class': 'market'})
        odds = [item.get_text() for item in odds]
        odds = [item for item in odds if item != "-"]
        return [(team, odd) for team, odd in zip(teams, odds)]

    def make_new_df(self, save):  # Top Level
        """
        overwriting the make_new_df method from the bool prop scraper for prop bets
        - makes a new df with all the current bets on ESB
        """
        df = self.create_df()
        title = self._get_sp_title()
        description = self._get_sp_description()
        bets = self._get_bets()
        scraped_ts = self._get_scrape_ts()
        for bet in bets:
            df.loc[len(df)] = [title, description, bet[0], bet[1], scraped_ts]
        if save:
            df.to_csv(self.df_path, index=False)
        return df

    def update_df(self):  # Run
        """
        Updates the existing bet df or creates a new one if this is a new bet
        """
        if not self.check_df_exists():
            self.make_new_df(save=True)
            print("-" * 25)
            print("New file created for {}".format(self.bet_name))
            print("-" * 25)
        else:
            current_df = pd.read_csv(self.df_path)
            new_df = self.make_new_df(save=False)
            drop_cols = ['Title', 'Team/Player']
            string_cols = ['Title', 'Team/Player', 'Odds']
            print_indices = [0, 1, 2]
            full_df = self.combine_dfs(current_df, new_df, drop_cols, string_cols, print_indices)
            full_df.to_csv(self.df_path, index=False)


if __name__ == "__main__":
    x = ESB_Prop_Scraper("NFL", "", None)
    self = x
    x.update_df()
