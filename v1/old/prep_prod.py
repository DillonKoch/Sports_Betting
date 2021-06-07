# ==============================================================================
# File: prep_prod.py
# Project: Modeling
# File Created: Thursday, 25th June 2020 4:36:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 27th July 2020 7:25:14 am
# Modified By: Dillon Koch
# -----
#
# -----
# This file prepares data from the PROD table for ML
# This is done for both finished games and games not yet played (for prediction)
# ==============================================================================


import json
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN_Scrapers.team_stats_scraper import Team_Stats


class Prep_Prod:
    def __init__(self, league: str):
        self.league = league
        self.football_league = True if self.league in ["NFL", "NCAAF"] else False

    @property
    def dash_cols(self):  # Property
        football_cols = ["penalties", "third_down_eff", "fourth_down_eff", "completions_attempts",
                         "redzone_made_att", "sacks_yards_lost"]
        basketball_cols = ["field_goals", "three_pointers", "free_throws"]
        cols = football_cols if self.football_league else basketball_cols
        cols = ["home_" + col if i % 2 == 0 else "away_" + col for i, col in
                enumerate([col for col in cols for i in range(2)])]
        return cols

    @property
    def config(self):  # Property
        with open(ROOT_PATH + "/Modeling/{}_model.json".format(self.league.lower())) as f:
            config = json.load(f)
        return config

    @property
    def stats_cols(self):  # Property
        ts = Team_Stats()
        cols = list(ts.football_dict.values()) if self.football_league else list(ts.basketball_dict.values())
        all_cols = ["home_" + col if i % 2 == 0 else "away_" + col for i,
                    col in enumerate([col for col in cols for i in range(2)])]
        return all_cols

    def load_prod_df(self):  # Top Level
        """
        loads the current PROD df in PROD folder, cleans names of teams that relocated
        """
        df = pd.read_csv(ROOT_PATH + "/PROD/{}_PROD.csv".format(self.league))
        df = df.replace("San Diego Chargers", "Los Angeles Chargers")
        df = df.replace("Oakland Raiders", "Las Vegas Raiders")
        df = df.replace("St. Louis Rams", "Los Angeles Rams")
        df = df.replace("Seattle SuperSonics", "Oklahoma City Thunder")
        df = df.replace("New Jersey Nets", "Brooklyn Nets")
        df = df.replace("Charlotte Bobcats", "Charlotte Hornets")
        df = df.replace("New Orleans Hornets", "New Orleans Pelicans")
        self.all_teams = set(list(df.Home) + list(df.Away))
        return df

    @staticmethod
    def normalize(nums):  # Global Helper
        nums = [float(item) for item in nums]
        min_num = np.min(nums)
        max_num = np.max(nums)
        return [((item - min_num) / (max_num - min_num)) for item in nums]

    def clean_week(self, prod_df):  # Top Level
        if self.league != "NFL":
            return prod_df
        prod_week_vals = list(prod_df.Week)
        prod_week_vals = [
            item.replace("WC", '18').replace("DIV", '19').replace("CONF", '20').replace("SB", '21') for item in prod_week_vals]
        prod_df.Week = pd.Series(self.normalize(prod_week_vals))
        return prod_df, ["Week"]

    def clean_season(self, prod_df):  # Top Level
        season_vals = list(prod_df.Season_x)
        prod_df.Season_x = pd.Series(self.normalize(season_vals))
        return prod_df, ["Season_x"]

    def clean_time_possession(self, prod_df):  # Specific Helper clean_stats
        prod_df['home_possession'] = prod_df['home_possession'].fillna("30:00")
        prod_df['away_possession'] = prod_df['away_possession'].fillna("30:00")

        def clean_row_TOP(row):
            for col in ['home', 'away']:
                col_name = "{}_possession".format(col)
                top_str = row[col_name]
                minutes, seconds = top_str.split(":")
                total_seconds = (int(minutes) * 60) + int(seconds)
                row[col_name] = total_seconds
            return row
        prod_df = prod_df.apply(lambda row: clean_row_TOP(row), axis=1)
        return prod_df

    def _expand_dash_stats(self, prod_df):  # Specific Helper clean_stats
        for col in self.dash_cols:
            prod_df[col] = prod_df[col].fillna("0-0")

        new_dash_cols = ["{}_d1".format(col) if i % 2 == 0 else "{}_d2".format(col)
                         for col in self.dash_cols for i in range(2)]
        for col in new_dash_cols:
            prod_df[col] = None

        def expand_row(row):
            for col in self.dash_cols:
                val1, val2 = row[col].split('-')
                row["{}_d1".format(col)] = int(val1)
                row["{}_d2".format(col)] = int(val2)
            return row
        prod_df = prod_df.apply(lambda row: expand_row(row), axis=1)
        return prod_df, new_dash_cols

    def _add_avg_stats_cols(self, prod_df, cols):  # Helping Helper _compute_stat_averages
        new_cols = ["avg_{}".format(col) for col in cols]
        for col in new_cols:
            prod_df[col] = None
        return prod_df, new_cols

    def _reset_stats_dict(self, cols):  # Helping Helper _compute_stat_averages
        dic = {team: {col: [] for col in cols} for team in self.all_teams}
        return dic

    def _new_stats_season_check(self, row, current_dict, current_season, cols):  # Helping Helper _compute_stat_averages
        is_new_season = True if int(row['Season_x']) > current_season else False
        if is_new_season:
            current_dict = self._reset_stats_dict(cols)
            current_season += 1
        return current_dict, current_season

    def _update_stats_row(self, row, stats_dict, comp_avg_cols):  # Helping Helper _compute_stat_average
        # updating the row with averages
        for item in ["Home", "Away"]:
            team = row[item]
            team_dict = stats_dict[team]
            for pair in team_dict.items():
                if item.lower() in pair[0]:
                    row["avg_" + pair[0]] = np.average(pair[1])
        return row

    def _update_stats_dict(self, stats_dict, row, comp_avg_cols):  # Helping Helper _compute_stat_average

        for item in ["Home", "Away"]:
            team = row[item]
            team_cols = [col for col in comp_avg_cols if item.lower() in col]
            for col in team_cols:
                stats_dict[team][col].append(row[col])
        return stats_dict

    def _compute_stat_averages(self, prod_df, comp_avg_cols):  # Specific Helper clean_stats
        prod_df, avg_col_names = self._add_avg_stats_cols(prod_df, comp_avg_cols)
        for col in comp_avg_cols:
            prod_df[col] = prod_df[col].fillna(0)

        stats_dict = self._reset_stats_dict(comp_avg_cols)
        current_season = int(prod_df.iloc[0, :]['Season_x'])

        for i, row in tqdm(prod_df.iterrows()):
            prod_df.iloc[i, :] = self._update_stats_row(row, stats_dict, comp_avg_cols)
            stats_dict = self._update_stats_dict(stats_dict, row, comp_avg_cols)
            stats_dict, current_season = self._new_stats_season_check(row, stats_dict, current_season, comp_avg_cols)

        return prod_df, avg_col_names

    def _scale_stats_cols(self, prod_df, avg_stats_cols):  # Specific Helper clean_stats
        scaler = MinMaxScaler()
        for col in avg_stats_cols:
            prod_df[col] = scaler.fit_transform(prod_df[col].values.reshape(-1, 1))
        return prod_df

    def clean_stats(self, prod_df):  # Top Level
        prod_df = self.clean_time_possession(prod_df)
        prod_df, new_dash_cols = self._expand_dash_stats(prod_df)
        comp_avg_cols = [item for item in self.stats_cols if item not in self.dash_cols] + new_dash_cols

        prod_df, avg_stats_cols = self._compute_stat_averages(prod_df, comp_avg_cols)
        prod_df = self._scale_stats_cols(prod_df, avg_stats_cols)
        return prod_df, avg_stats_cols

    def add_dummies(self, df, prod_df):  # Top Level
        dummy_cols = ["Home", "Away", "Network"]
        for col in dummy_cols:
            new_dummy_df = pd.get_dummies(prod_df[col], prefix=col)
            df = pd.concat([df, new_dummy_df], axis=1)
        return df

    def get_target_data(self, prod_df):  # Top Level
        # create a df the same size as the input data that has the target features
        target_cols = ["Home_Score_x", "Away_Score_x", "HQ1_x", "HQ2_x", "HQ3_x", "HQ4_x", "HOT", "AQ1_x", "AQ2_x",
                       "AQ3_x", "AQ4_x", "AOT",
                       "Home_ML", "Away_ML", "Open_OU", "Close_OU", "2H_OU", "Open_Home_Line", "Open_Away_Line",
                       "Close_Home_Line", "Close_Away_Line", "2H_Home_Line", "2H_Away_Line",
                       "Over_ESB", "Over_ml_ESB", "Under_ESB", "Under_ml_ESB", "Home_Line_ESB", "Home_Line_ml_ESB",
                       'Away_Line_ESB', 'Away_Line_ml_ESB', 'Home_ML_ESB', 'Away_ML_ESB']
        target_cols = [item for item in target_cols if item in list(prod_df.columns)]
        target_df = prod_df.loc[:, target_cols]
        return target_df

    def run(self, save_local=False):  # Run
        """
        starting with a blank df and prod df, then as I clean and modify each section of PROD for ML,
        I'll also update my ML dataset at that time
        """
        prod_df = self.load_prod_df()
        prod_df, record_ml_cols = self.clean_prod_records(prod_df)
        prod_df, week_ml_cols = self.clean_week(prod_df)
        prod_df, season_ml_cols = self.clean_season(prod_df)
        prod_df, stats_ml_cols = self.clean_stats(prod_df)

        df = pd.DataFrame()
        df = self.add_dummies(df, prod_df)
        df['datetime'] = prod_df['datetime']
        df['Final_Status'] = prod_df['Final_Status']
        ml_cols = record_ml_cols + week_ml_cols + season_ml_cols + stats_ml_cols
        prod_ml = prod_df.loc[:, ml_cols]

        df = pd.concat([df, prod_ml], axis=1)
        target_df = self.get_target_data(prod_df)

        if save_local:
            df.to_csv("{}_ml.csv".format(self.league.lower()), index=False)
            target_df.to_csv("{}_target.csv".format(self.league.lower()), index=False)
        return df, target_df


if __name__ == "__main__":
    nfl = Prep_Prod("NFL")
    nba = Prep_Prod("NBA")
    ncaaf = Prep_Prod("NCAAF")
    ncaab = Prep_Prod("NCAAB")
    self = nba
    # df, target_df = self.run(save_local=True)


# idea for showing average stats:
    # compute the running average for each week like with wins and losses
    # then for week 1 of the following year, use the average I have from the last year
    # just don't reset the dict until after using the values for week 1 of the new year
