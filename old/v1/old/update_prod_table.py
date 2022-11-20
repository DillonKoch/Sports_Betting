# ==============================================================================
# File: update_prod_table.py
# Project: PROD
# File Created: Wednesday, 24th June 2020 5:15:01 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 29th June 2020 4:16:35 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File to update any of the PROD csv's - pull newly scraped data, add game results/stats
# UPDATE PROD WILL NOT DO ANYTHING THAT CREATING PROD FROM SCRATCH WON'T DO
# THIS FILE WILL JUST UPDATE THE PROD TABLE WITH NEW RESULTS AND SKIP THE WORK ALREADY DONE
# THIS FILE DOES NOT CREATE/SCRAPE NEW DATA, JUST PULL IT IN FROM ESPN/ESB/ODDS LOCATIONS
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN_Scrapers.espn_game_scraper import ESPN_Game_Scraper


class Update_Prod:
    def __init__(self, league):
        self.league = league
        self.prod_path = ROOT_PATH + "/PROD/{}_PROD.csv".format(self.league)

    @property
    def game_scraper_func(self):  # Property
        egs = ESPN_Game_Scraper()
        nba = egs.all_nba_info
        nfl = egs.all_nfl_info
        ncaaf = egs.all_ncaaf_info
        ncaab = egs.all_ncaab_info
        return nba if self.league == "NBA" else nfl if self.league == "NFL" else ncaaf if self.league == "NCAAF" else ncaab

    def _update_row(self, row):  # Specific Helper udpate_game_results
        espn_id = row['ESPN_ID']
        game = self.game_scraper_func(espn_id)

        row = [game.ESPN_ID, row["Season"], game.game_date, game.home_name, game.away_name,
               game.home_record, game.away_record,
               game.home_score, game.away_score, game.line, game.over_under,
               game.final_status, game.network]

    def update_game_results(self, df):  # Top Level
        for i, row in df.iterrows():
            if "Final" not in row['Final_Status']:
                df.iloc[i, :] = self._update_row(row)
        return df

    def update_team_stats(self, df):  # Top Level
        pass

    def update_esb_odds(self, df):  # Top Level
        pass

    def run(self):  # Run
        df = pd.read_csv(self.prod_path)
        df = self.update_game_results(df)
        df = self.update_team_stats(df)
        df = self.update_esb_odds(df)
        df.to_csv(self.prod_path, index=False)


if __name__ == "__main__":
    x = Update_Prod("NFL")
