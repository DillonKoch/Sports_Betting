# ==============================================================================
# File: espn_update_results_scraper.py
# Project: ESPN
# File Created: Saturday, 5th September 2020 10:13:47 am
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 5th September 2020 11:31:12 am
# Modified By: Dillon Koch
# -----
#
# -----
# scraper for updating the resuls of recently finished games in ESPN data
# ==============================================================================


import datetime
import sys
import time
import warnings
from os.path import abspath, dirname

import pandas as pd

warnings.filterwarnings('ignore')

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN.espn_game_scraper import ESPN_Game_Scraper
from Utility.Utility import parse_league, sort_df_by_dt


class Update_Results_Scraper:
    """
    class for updating the main ESPN results in each league's csv
    """

    def __init__(self, league):
        self.league = league
        self.df_path = ROOT_PATH + f"/ESPN/Data/{self.league}.csv"
        self.egs = ESPN_Game_Scraper(self.league)

    def filter_finished_games(self, df):  # Top Level
        """
        filters out the games already finished from the df
        """
        final_mask = df['Final_Status'].str.contains('Final')
        final_mask.fillna(False, inplace=True)
        new_df = df.loc[~final_mask]
        return new_df

    def filter_by_date(self, df):  # Top Level
        """
        filters out the games that haven't happened yet from the df
        """
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['datetime'] = df['datetime'].dt.date
        today = datetime.date.today()
        new_df = df.loc[df.datetime < today]
        return new_df

    def update_results(self, df):  # Top Level
        """
        given a df with finished games that need to be updated, this will scrape the
        game's data and update the small df
        """
        def update_row(row):
            espn_id = int(row['ESPN_ID'])
            game = self.egs.run(espn_id)
            time.sleep(5)
            week = row['Week'] if self.league == "NFL" else None
            new_game_info = game.to_row_list(self.league, row['Season'], week)
            row[:len(new_game_info)] = new_game_info
            print("{}: {}, {}: {}".format(row['Home'], row['Home_Score'],
                                          row['Away'], row['Away_Score']))
            return row

        df = df.apply(lambda row: update_row(row), axis=1)
        return df

    def merge_dfs(self, original_df, update_df):  # Top Level
        """
        merges the unchanged original df, and the df of only updated games
        - replaces rows in original_df with updated ones in update_df
        """
        full_df = pd.concat([original_df, update_df])
        full_df.drop_duplicates(subset=['ESPN_ID'], keep='last', inplace=True)
        full_df = sort_df_by_dt(full_df, keep_dt=True)
        return full_df

    def run(self):  # Run
        original_df = pd.read_csv(self.df_path)
        update_df = self.filter_finished_games(original_df)
        update_df = self.filter_by_date(update_df)
        update_df = self.update_results(update_df)
        full_df = self.merge_dfs(original_df, update_df)
        full_df.to_csv(self.df_path, index=False)
        print(f"\n{self.league} ESPN data saved!\n")
        return full_df


if __name__ == '__main__':
    league = parse_league()
    x = Update_Results_Scraper(league)
    self = x
    df = x.run()
