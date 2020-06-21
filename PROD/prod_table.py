# ==============================================================================
# File: prod_table.py
# Project: PROD
# File Created: Thursday, 18th June 2020 12:48:04 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 21st June 2020 8:19:26 am
# Modified By: Dillon Koch
# -----
#
# -----
# Program to create and update the season PROD table for each league
# As new data from ESPN, odds, ESB odds are available, this will update the prod csv
# ==============================================================================

import datetime
import json
import os
import sys
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Prod_Table:
    def __init__(self, league):
        self.league = league
        self.prod_table = ROOT_PATH + "/PROD/PROD_{}.csv".format(self.league)
        self.config_file = ROOT_PATH + "/PROD/{}_prod.json".format(self.league.lower())
        self.teams = os.listdir(ROOT_PATH + "/ESPN_Data/{}/".format(self.league))

    @property
    def config(self):  # Property
        with open(self.config_file) as f:
            config = json.load(f)
        return config

    @property
    def season_start_dict(self):  # Property
        config_dict = self.config['season_start_dates']
        years = [str(item) for item in range(2007, 2020)]
        dic = {year: datetime.date(config_dict[year][0], config_dict[year][1], config_dict[year][2]) for year in years}
        return dic

    def _show_team_dfs_dict(self):  # Global Helper not used in run(), but helpful
        team_dict = {team: 0 for team in self.teams}
        df_paths = self._get_df_paths()
        for item in df_paths:
            for team in self.teams:
                if team in item:
                    team_dict[team] += 1
        return team_dict

    def check_table_exists(self):  # Top Level  Tested
        path = ROOT_PATH + "/PROD/"
        exists = True if self.prod_table in os.listdir(path) else False
        return exists

    def create_dataframe(self):  # Top Level  Tested
        cols = self.config["ESPN_cols"]
        df = pd.DataFrame(columns=cols)
        return df

    def load_prod_df(self):  # Top Level  Tested
        df = pd.read_csv(self.prod_table)
        return df

    def _get_df_paths(self):  # Specific Helper load_espn_data Tested
        df_paths = []
        for team in self.teams:
            team_paths = [item for item in os.listdir(ROOT_PATH + "/ESPN_Data/{}/{}/".format(self.league, team))]
            team_paths = [item for item in team_paths if (('.csv' in item) and (int(item[-8:-4]) > 2007))]
            team_paths = [ROOT_PATH + "/ESPN_Data/{}/{}/{}".format(self.league, team, item) for item in team_paths]
            df_paths += team_paths
        return df_paths

    def _load_all_team_dfs(self, df_paths):  # Specific Helper load_espn_data Tested
        all_team_dfs = []
        for path in tqdm(df_paths):
            current_df = pd.read_csv(path)
            current_df = current_df[current_df.Home.notnull()]
            current_df = current_df[current_df.Final_Status.notnull()]
            if len(current_df) > 0:
                all_team_dfs.append(current_df)
        return all_team_dfs

    def _add_datetime(self, df):  # Helping Helper _remove_preseason Tested
        def add_dt(row):
            return datetime.datetime.strptime(row['Date'], "%B %d, %Y")
        df['datetime'] = df.apply(lambda row: add_dt(row), axis=1)
        df['datetime'] = pd.to_datetime(df['datetime']).apply(lambda x: x.date())
        return df

    def _remove_preseason(self, df):  # Specific Helper load_espn_data  Tested
        if self.league == "NFL":
            year = str(int(df.Season[0]))
            start_date = self.season_start_dict[year]
            df = df.loc[df.datetime >= start_date]
        return df

    def _clean_concat_team_dfs(self, all_team_dfs):  # Specific Helper load_espn_data  Tested
        full_df = pd.concat(all_team_dfs)
        full_df.drop_duplicates(subset="ESPN_ID", inplace=True)
        full_df.sort_values(by="datetime", inplace=True)
        return full_df

    def load_espn_data(self):  # Top Level  Tested
        df_paths = self._get_df_paths()
        all_team_dfs = self._load_all_team_dfs(df_paths)
        all_team_dfs = [self._add_datetime(df) for df in all_team_dfs]
        all_team_dfs = [self._remove_preseason(df) for df in all_team_dfs]
        espn_df = self._clean_concat_team_dfs(all_team_dfs)
        espn_df = espn_df.loc[:, self.config["ESPN_cols"] + ["datetime"]]
        return espn_df

    def add_espn_stats_data(self):  # Top Level
        pass

    def add_odds_data(self):  # Top Level
        pass

    def add_esb_data(self):  # Top Level
        pass

    # def run(self):  # Run
    #     exists = self.check_table_exists()
    #     df = self.load_prod_df() if exists else self.create_dataframe()
    #     return df

    def prod_table_from_scratch(self):  # Run
        df = self.create_dataframe()

    def update_prod_table(self):  # Run
        pass


if __name__ == "__main__":
    x = Prod_Table("NCAAF")
    self = x
    # df = x.run()
    espn_df = x.load_espn_data()
    espn_df.to_csv("temp_ncaab.csv")
