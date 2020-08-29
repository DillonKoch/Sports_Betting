# ==============================================================================
# File: espn_update_results.py
# Project: ESPN_Scrapers
# File Created: Tuesday, 30th June 2020 11:58:42 am
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 1st August 2020 4:18:53 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraper for updating results of games in ESPN_Data folder that have finished or been updated
# ==============================================================================
# Goal is to update final scores and team stats quickly and efficiently


import datetime
import sys
from os.path import abspath, dirname
import time
import json

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN_Scrapers.espn_game_scraper import ESPN_Game_Scraper
from ESPN_Scrapers.team_stats_scraper import Team_Stats
from Utility.Utility import parse_league, sort_df_by_dt, listdir_fullpath


class ESPN_Update_Results:
    """
     Updates the games in ESPN_Data that have been updated or played
    """

    def __init__(self, league):
        self.league = league
        self.egs = ESPN_Game_Scraper(self.league)

    @property
    def config(self):  # Property
        with open("{}.json".format(self.league.lower())) as f:
            config = json.load(f)
        return config

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

    @property
    def season_start_dict(self):  # Property
        config_dict = self.config['season_start_dates']
        years = [str(item) for item in range(2007, 2021)]
        dic = {year: datetime.date(config_dict[year][0], config_dict[year][1], config_dict[year][2]) for year in years}
        return dic

    def load_dfs(self):  # Top Level
        """
        loads all team dfs in a leauge's ESPN_Data folder
        """
        df_paths = listdir_fullpath(ROOT_PATH + "/ESPN_Data/{}/".format(self.league))
        dfs = [pd.read_csv(df_path) for df_path in df_paths]
        for df in dfs:
            df['datetime'] = pd.to_datetime(df['datetime']).apply(lambda x: x.date())
        return dfs, df_paths

    def _add_datetime(self, df):  # Specific Helper remove_preseason
        """
        adds datetime in %B %d, %Y format to a dataframe, if it's not there already
        """
        if df['datetime'].isnull().sum() == 0:
            return df

        def add_dt(row):
            return datetime.datetime.strptime(row['Date'], "%B %d, %Y")
        df['datetime'] = df.apply(lambda row: add_dt(row), axis=1)
        df['datetime'] = pd.to_datetime(df['datetime']).apply(lambda x: x.date())
        return df

    def remove_preseason(self, df):  # Top Level
        """
        only used in NFL - removes the preseason games from espn data
        """
        df = self._add_datetime(df)
        if self.league == "NFL":

            def add_preseason(row):
                year = str(int(row['Season']))
                start_date = self.season_start_dict[year]
                return row['datetime'] < start_date

            df['is_preseason'] = df.apply(lambda row: add_preseason(row), axis=1)
            df = df.loc[df.is_preseason == False, :]
            df = df.drop("is_preseason", axis=1)
        return df

    def update_game_results(self, df):  # Top Level
        """
        updates team's csv's in a league folder for games that have recently finished
        - also updates games less than one week away, so current records are scraped
        """
        def update_row_results(row):
            if "Final" in str(row["Final_Status"]):
                return row

            in_one_week = datetime.date.today() + datetime.timedelta(days=7)
            if row['datetime'] > in_one_week:
                return row

            espn_id = str(int(row['ESPN_ID']))
            game = self.egs.run(espn_id)
            time.sleep(5)
            week = row['Week'] if self.league == "NFL" else None
            new_game_info = game.to_row_list(self.league, row['Season'], week)
            row[:len(new_game_info)] = new_game_info
            print("{} ({}): {}, {} ({}): {}".format(row['Home'], row['Home_Record'], row['Home_Score'],
                                                    row['Away'], row['Away_Record'], row['Away_Score']))
            return row

        df = df.apply(lambda row: update_row_results(row), axis=1)
        return df

    def save_dfs(self, dfs, df_paths):  # Top Level
        """
        saves all dfs to the right df path in run() method
        """
        for df, df_path in zip(dfs, df_paths):
            df.to_csv(df_path, index=False)
        print("ALL {} DATA SAVED".format(self.league))

    def run(self):  # Run
        dfs, df_paths = self.load_dfs()
        for df, df_path in zip(dfs, df_paths):
            print("updating {}...".format(df_path.split("/")[-1]))
            df = self.update_game_results(df)
            df = self.remove_preseason(df)
            df = sort_df_by_dt(df, keep_dt=True)
            df.to_csv(df_path, index=False)
            print("\n" + ("-" * 25))
            print("{} saved!".format(df_path.split("/")[-1]))
            print(("-" * 25) + "\n")
        print(f"Finished updating {self.league} games!")


if __name__ == "__main__":
    league = parse_league()
    x = ESPN_Update_Results(league)
    dfs = x.run()
