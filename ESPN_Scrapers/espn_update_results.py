# ==============================================================================
# File: espn_update_results.py
# Project: ESPN_Scrapers
# File Created: Tuesday, 30th June 2020 11:58:42 am
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 1st July 2020 4:02:13 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraper for updating results of games in ESPN_Data folder that have finished or been updated
# ==============================================================================
# Goal is to update final scores and team stats quickly and efficiently


import datetime
import os
import sys
from os.path import abspath, dirname
import time

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN_Scrapers.espn_game_scraper import ESPN_Game_Scraper
from ESPN_Scrapers.team_stats_scraper import Team_Stats
from Utility.Utility import parse_league


class ESPN_Update_Results:
    """
     Updates the games in ESPN_Data that have been updated or played
    """

    def __init__(self, league):
        self.league = league
        self.egs = ESPN_Game_Scraper(self.league)

    @property
    def football_cols(self):  # Property
        ts = Team_Stats()
        stats_items = list(ts.football_dict.values())
        football_cols = []
        for stat in stats_items:
            football_cols.append("home_" + stat)
            football_cols.append("away_" + stat)
        return football_cols

    @property
    def basketball_cols(self):  # Property
        ts = Team_Stats()
        stats_items = list(ts.basketball_dict.values())
        basketball_cols = []
        for stat in stats_items:
            basketball_cols.append("home_" + stat)
            basketball_cols.append("away_" + stat)
        return basketball_cols

    def load_dfs(self):  # Top Level
        df_paths = [ROOT_PATH + "/ESPN_Data/{}/".format(self.league) + path for path in
                    os.listdir(ROOT_PATH + "/ESPN_Data/{}/".format(self.league))]
        dfs = [pd.read_csv(df_path) for df_path in df_paths]
        return dfs, df_paths

    def update_game_results(self, df):
        def update_row_results(row):
            if "Final" in str(row["Final_Status"]):
                return row
            if datetime.datetime.strptime(row['Date'], "%B %d, %Y") > datetime.datetime.now():
                return row

            game = self.egs.run(row['ESPN_ID'])
            time.sleep(3)
            new_game_info = game.to_row_list(self.league, row['Season'])
            row[:len(new_game_info)] = new_game_info
            print("{}: {}, {}: {}".format(row['Home'], row['Home_Score'], row['Away'], row['Away_Score']))
            return row

        df = df.apply(lambda row: update_row_results(row), axis=1)
        return df

    def update_team_stats(self):
        def update_row_stats(row):
            pass

    def update_records(self):
        pass

    def save_dfs(self, dfs, df_paths):  # Top Level
        for df, df_path in zip(dfs, df_paths):
            df.to_csv(df_path, index=False)
        print("ALL DATA SAVED")

    def run(self):  # Run
        dfs, df_paths = self.load_dfs()
        dfs = [self.update_game_results(df) for df in dfs]
        self.save_dfs(dfs, df_paths)
        return dfs


if __name__ == "__main__":
    league = parse_league() if False else "NBA"
    x = ESPN_Update_Results(league)
    self = x

    dfs = x.run()
