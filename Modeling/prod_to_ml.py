# ==============================================================================
# File: prod_to_ml.py
# Project: Modeling
# File Created: Tuesday, 14th July 2020 4:47:07 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 27th July 2020 10:59:38 am
# Modified By: Dillon Koch
# -----
#
# -----
# Agent for converting a row from a PROD df to ML-usable data
# (this is replacing the former method of using dictionaries and df.iterrows()
# for updating the records and average team stats)
# ==============================================================================


import datetime
import json
import sys
import time
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from sklearn import preprocessing
from tqdm import tqdm


tqdm.pandas()

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN_Scrapers.team_stats_scraper import Team_Stats


class Prod_to_ML:
    def __init__(self, league: str):
        self.league = league
        self.football_league = True if self.league in ["NFL", "NCAAB"] else False

    @property
    def config(self):  # Property
        with open(ROOT_PATH + "/Modeling/{}_model.json".format(self.league.lower())) as f:
            config = json.load(f)
        return config

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
    def new_dash_cols(self):  # Property
        new_dash_cols = ["{}_d1".format(col) if i % 2 == 0 else "{}_d2".format(col)
                         for col in self.dash_cols for i in range(2)]
        return new_dash_cols

    @property
    def stats_cols(self):  # Property
        ts = Team_Stats()
        cols = list(ts.football_dict.values()) if self.football_league else list(ts.basketball_dict.values())
        all_cols = ["home_" + col if i % 2 == 0 else "away_" + col for i,
                    col in enumerate([col for col in cols for i in range(2)])]
        return all_cols

    @property
    def ml_stats_cols(self):  # Property
        cols = [col for col in self.stats_cols if col not in self.dash_cols]
        ml_stats_cols = cols + self.new_dash_cols
        return ml_stats_cols

    def _replace_relocated_teams(self, df):  # Specific Helper load_prod_df
        df = df.replace("San Diego Chargers", "Los Angeles Chargers")
        df = df.replace("Oakland Raiders", "Las Vegas Raiders")
        df = df.replace("St. Louis Rams", "Los Angeles Rams")
        df = df.replace("Seattle SuperSonics", "Oklahoma City Thunder")
        df = df.replace("New Jersey Nets", "Brooklyn Nets")
        df = df.replace("Charlotte Bobcats", "Charlotte Hornets")
        df = df.replace("New Orleans Hornets", "New Orleans Pelicans")
        return df

    def _add_prod_cols(self, prod_df):  # Specific Helper load_prod_df
        """
        adds columns to the prod df to help create ml cols
        """

        def is_conf(row):
            return True if "Conf" in str(row['Home_Record']) else False

        def is_neutral(row):
            home_record = str(row['Home_Record'])
            if home_record == "nan":
                return False
            has_conf = True if "Conf" in home_record else False
            has_home = True if "Home" in home_record else False
            return False if ((has_conf) or (has_home)) else True

        def tie_game(row):
            home_score = str(row['Home_Score_x'])
            away_score = str(row['Away_Score_x'])
            if home_score == "nan":
                return False
            return True if float(home_score) == float(away_score) else False

        def home_won(row):
            home_score = str(row['Home_Score_x'])
            away_score = str(row['Away_Score_x'])
            if home_score == "nan":
                return None
            return True if float(home_score) > float(away_score) else False

        prod_df['datetime'] = pd.to_datetime(prod_df['datetime']).apply(lambda x: x.date())
        prod_df['conf_game'] = prod_df.apply(lambda row: is_conf(row), axis=1)
        prod_df['neutral_game'] = prod_df.apply(lambda row: is_neutral(row), axis=1)
        prod_df['tie'] = prod_df.apply(lambda row: tie_game(row), axis=1)
        prod_df['Home_won'] = prod_df.apply(lambda row: home_won(row), axis=1)
        return prod_df

    def _expand_dash_cols(self, df):  # Specific Helper load_prod_df
        """
        separates stats columns with a dash into two columns
        - e.g. completions-attempts 22-31 --> two cols 22, 31
        """
        for col in self.dash_cols:
            df[col] = df[col].fillna("0-0")

        for col in self.new_dash_cols:
            df[col] = None

        def expand_row(row):
            for col in self.dash_cols:
                val1, val2 = row[col].split('-')
                row["{}_d1".format(col)] = int(val1)
                row["{}_d2".format(col)] = int(val2)
            return row
        df = df.apply(lambda row: expand_row(row), axis=1)
        return df

    def _clean_time_possession(self, df):  # Specific Helper load_prod_df
        """
        changes Time of Possession into total seconds instead of min:sec (30:00) format
        """
        if not self.football_league:
            return df
        df['home_possession'] = df['home_possession'].fillna("30:00")
        df['away_possession'] = df['away_possession'].fillna("30:00")

        def clean_row_TOP(row):
            for col in ['home', 'away']:
                col_name = "{}_possession".format(col)
                top_str = row[col_name]
                minutes, seconds = top_str.split(":")
                total_seconds = (int(minutes) * 60) + int(seconds)
                row[col_name] = total_seconds
            return row
        df = df.apply(lambda row: clean_row_TOP(row), axis=1)
        return df

    def load_prod_df(self):  # Top Level
        """
        loads the PROD dataframe and cleans it before creating any ml cols
        """
        df = pd.read_csv(ROOT_PATH + "/PROD/{}_PROD.csv".format(self.league.upper()))
        df = self._replace_relocated_teams(df)
        df = self._add_prod_cols(df)
        df = self._expand_dash_cols(df)
        df = self._clean_time_possession(df)
        return df

    def _get_relevant_data(self, prod_df, team_name: str, season: int, game_date: datetime):  # Specific Helper get_record
        """
        returns df of relevant data for the team_name/season/game_date combo
        - relevant data is either (1) games already played in the given season, or
          (2) games from the previous season if the input season has not begun
        """
        df = prod_df.loc[prod_df.Season_x == int(season)]
        df = df.loc[(df.Home == team_name) | (df.Away == team_name)]
        df = df.loc[df.datetime < game_date]
        df = df.loc[df.Final_Status.notnull()]
        if ((len(df) == 0) and (season > 2007)):
            return self._get_relevant_data(prod_df, team_name, season - 1, game_date)
        return df

    def _get_specific_record(self, df, home: bool):  # Specific Helper get_record
        results = list(df['Home_won'])
        wins = results.count(True) if home else results.count(False)
        losses = results.count(False) if home else results.count(True)
        ties = list(df['tie']).count(True)
        return wins, losses, ties

    def get_record(self, prod_df, team_name: str, season: int, game_date: datetime, home: bool, neutral=False):  # Top Level
        """
        returns the 6 record values (below) for a team from the dataframe input
        (ovr_wins, ovr_losses, ovr_ties, spec_wins, spec_losses, spec_ties)
        - spec w/l/t is only neutral/home/away at the moment, not conference games
        """
        df = self._get_relevant_data(prod_df, team_name, season, game_date)

        home_df = df.loc[(df.Home == team_name) & (df.neutral_game == False)]
        home_wins, home_losses, home_ties = self._get_specific_record(home_df, home=True)

        away_df = df.loc[(df.Away == team_name) & (df.neutral_game == False)]
        away_wins, away_losses, away_ties = self._get_specific_record(away_df, home=False)

        home_neutral_df = df.loc[(df.Home == team_name) & (df.neutral_game == True)]
        home_neutral_wins, home_neutral_losses, home_neutral_ties = self._get_specific_record(home_neutral_df, home=True)

        away_neutral_df = df.loc[(df.Away == team_name) & (df.neutral_game == True)]
        away_neutral_wins, away_neutral_losses, away_neutral_ties = self._get_specific_record(away_neutral_df, home=False)

        neutral_wins = home_neutral_wins + away_neutral_wins
        neutral_losses = home_neutral_losses + away_neutral_losses
        neutral_ties = home_neutral_ties + away_neutral_ties

        ovr_wins = home_wins + away_wins + home_neutral_wins + away_neutral_wins
        ovr_losses = home_losses + away_losses + home_neutral_losses + away_neutral_losses
        ovr_ties = home_ties + away_ties + home_neutral_ties + away_neutral_ties

        spec_wins = neutral_wins if neutral else home_wins if home else away_wins
        spec_losses = neutral_losses if neutral else home_losses if home else away_losses
        spec_ties = neutral_ties if neutral else home_ties if home else away_ties

        return ovr_wins, ovr_losses, ovr_ties, spec_wins, spec_losses, spec_ties

    def add_records(self, ml_df, prod_df):  # Top Level
        """
        Adds team records for games in the prod_df to ml_df
        - requires full prod_df to calculate full records
        """
        print("Adding records to the dataframe...")
        time.sleep(1)
        cols = ["ovr_wins", "ovr_losses", "ovr_ties", "spec_wins", "spec_losses", "spec_ties"]
        home_cols = ["home_" + item for item in cols]
        away_cols = ["away_" + item for item in cols]
        all_record_cols = home_cols + away_cols

        def add_row_records(row, all_record_cols):
            home_team = row['Home']
            away_team = row['Away']
            season = int(row['Season_x'])
            game_date = row['datetime']
            neutral_game = row['neutral_game']

            home_record_vals = self.get_record(prod_df, home_team, season, game_date, home=True, neutral=neutral_game)
            away_record_vals = self.get_record(prod_df, away_team, season, game_date, home=False, neutral=neutral_game)

            for col in all_record_cols:
                row[col] = None

            for col, val in zip(home_cols, home_record_vals):
                row[col] = val

            for col, val in zip(away_cols, away_record_vals):
                row[col] = val

            return row

        prod_df = prod_df.progress_apply(lambda row: add_row_records(row, all_record_cols), axis=1)
        record_df = prod_df.loc[:, all_record_cols]
        df = pd.concat([ml_df, record_df], axis=1)
        return df

    def _get_specific_stats(self, df, home: bool):
        home_away_str = "home" if home else "away"
        cols = [col for col in self.ml_stats_cols if home_away_str in col]
        avg_stats = []
        for col in cols:
            vals = list(df[col])
            avg = np.average(vals)
            avg_stats.append(avg)
        # return avg_stats if "nan" not in [str(i) for i in avg_stats] else None
        # this line^ made it so we didn't get NBA stats from 2012-2015 becuase there
        # was no largest lead value
        # return avg_stats
        avg_stats = [item if str(item) != "nan" else -1 for item in avg_stats]
        return avg_stats

    def get_team_stats(self, df, team_name: str, season: int, game_date: datetime, home: bool, neutral=False):  # Top Level
        """
        returns the avg stats values for a team from the dataframe input
        - format: overall avg_stats_cols, spec_avg_stats_cols (just like record)
        - football: x cols
        - basketball: x cols
        """
        df = self._get_relevant_data(df, team_name, season, game_date)

        home_df = df.loc[(df.Home == team_name) & (df.neutral_game == False)]
        home_stats = self._get_specific_stats(home_df, home=True)

        away_df = df.loc[(df.Away == team_name) & (df.neutral_game == False)]
        away_stats = self._get_specific_stats(away_df, home=False)

        home_neutral_df = df.loc[(df.Home == team_name) & (df.neutral_game == True)]
        home_neutral_stats = self._get_specific_stats(home_neutral_df, home=True)

        away_neutral_df = df.loc[(df.Away == team_name) & (df.neutral_game == True)]
        away_neutral_stats = self._get_specific_stats(away_neutral_df, home=False)

        ovr_stat_list = [lis for lis in [home_stats, away_stats, home_neutral_stats, away_neutral_stats]
                         if lis is not None]
        ovr_stats = [np.average(x) for x in zip(*ovr_stat_list)]

        neutral_stat_list = [lis for lis in [home_neutral_stats, away_neutral_stats] if lis is not None]
        neutral_stats = [np.average(x) for x in zip(*neutral_stat_list)]

        spec_stats = neutral_stats if neutral else home_stats if home else away_stats
        spec_stats = ovr_stats if ((spec_stats is None) or (spec_stats == [])) else spec_stats

        return ovr_stats, spec_stats

    def add_team_stats(self, ml_df, prod_df):  # Top Level
        """
        Calculates team stats for games in the prod_df, then adds them to ml_df
        - requires full prod_df to calculate avg stats
        """
        print("calculating average team stats...")
        time.sleep(1)
        home_ml_cols = [col for col in self.ml_stats_cols if "home" in col]
        avg_home_cols = ["ovr_avg_" + c for c in home_ml_cols] + ["spec_avg_" + c for c in home_ml_cols]

        away_ml_cols = [col for col in self.ml_stats_cols if "away" in col]
        avg_away_cols = ["ovr_avg_" + c for c in away_ml_cols] + ["spec_avg_" + c for c in away_ml_cols]
        new_stats_cols = avg_home_cols + avg_away_cols

        def add_avg_stats(row, new_stats_cols):
            home_team = row['Home']
            away_team = row['Away']
            season = int(row['Season_x'])
            game_date = row['datetime']
            neutral_game = row['neutral_game']

            home_ovr_stats, home_spec_stats = self.get_team_stats(prod_df, home_team, season,
                                                                  game_date, home=True, neutral=neutral_game)
            away_ovr_stats, away_spec_stats = self.get_team_stats(prod_df, away_team, season,
                                                                  game_date, home=False, neutral=neutral_game)
            new_col_vals = home_ovr_stats + home_spec_stats + away_ovr_stats + away_spec_stats
            for col in new_stats_cols:
                row[col] = None

            for col, val in zip(new_stats_cols, new_col_vals):
                row[col] = val
            return row

        prod_df = prod_df.progress_apply(lambda row: add_avg_stats(row, new_stats_cols), axis=1)
        stats_df = prod_df.loc[:, new_stats_cols]
        df = pd.concat([ml_df, stats_df], axis=1)
        return df

    def clean_missing_team_stats(self, ml_df):  # Top Level
        """
        missing values from ESPN are recorded as -1, so we're replacing those -1's with
        the average value from the column (ignoring -1's)
        """
        stats_cols = [col for col in list(ml_df.columns) if "avg" in col]
        for col in stats_cols:
            values = list(ml_df[col])
            values = [item if item >= 0 else -1 for item in values]
            ml_df[col] = pd.Series(values)
            positive_values = [val for val in values if val != -1]
            avg_value = np.average(positive_values)
            ml_df[col] = ml_df[col].replace(-1, avg_value)
        return ml_df

    def add_dummies(self, ml_df, prod_df):  # Top Level
        """
        adds dummy columns from the prod_df to the ml_df
        """
        dummy_cols = ["Home", "Away", "Network"]
        for col in dummy_cols:
            new_dummy_df = pd.get_dummies(prod_df[col], prefix=col)
            ml_df = pd.concat([ml_df, new_dummy_df], axis=1)
        return ml_df

    def add_binary_cols(self, ml_df, prod_df):  # Top Level
        """
        adds binary cols created from the prod_df to the ml_df
        """
        ml_df['neutral_game'] = prod_df['neutral_game'].astype(int)
        ml_df['conf_game'] = prod_df['conf_game'].astype(int)
        return ml_df

    def add_season(self, ml_df, prod_df):  # Top Level
        ml_df['Season'] = prod_df['Season_x'].astype(int)
        return ml_df

    def add_week(self, ml_df, prod_df):  # Top Level
        """
        adds the week to ml_df if the league is NFL, otherwise does nothing
        """
        if self.league != "NFL":
            return ml_df

        prod_weeks = list(prod_df['Week'])
        prod_weeks = [item.replace("WC", '18').replace("DIV", "19").replace("CONF", "20").replace("SB", "21")
                      for item in prod_weeks]
        ml_df['Week'] = pd.Series(prod_weeks).astype(int)
        return ml_df

    def normalize_full_df(self, df):  # Top Level
        cols = ["ESPN_ID", "datetime", "Final_Status"]
        norm_cols = [col for col in list(df.columns) if col not in cols]
        no_change_df = df.loc[:, cols]
        norm_df = df.loc[:, norm_cols]

        x = norm_df.values
        min_max_scaler = preprocessing.MinMaxScaler()
        x_scaled = min_max_scaler.fit_transform(x)
        norm_df = pd.DataFrame(x_scaled, columns=norm_cols)
        full_df = pd.concat([no_change_df, norm_df], axis=1)
        return full_df

    def run(self, normalize=True):  # Run
        prod_df = self.load_prod_df()

        ml_df = pd.DataFrame()
        ml_df['ESPN_ID'] = prod_df['ESPN_ID']
        ml_df['datetime'] = prod_df['datetime']
        ml_df['Final_Status'] = prod_df['Final_Status']
        ml_df = self.add_dummies(ml_df, prod_df)
        ml_df = self.add_binary_cols(ml_df, prod_df)
        ml_df = self.add_season(ml_df, prod_df)
        ml_df = self.add_week(ml_df, prod_df)
        ml_df = self.add_records(ml_df, prod_df)
        ml_df = self.add_team_stats(ml_df, prod_df)
        ml_df = self.clean_missing_team_stats(ml_df)
        if normalize:
            ml_df = self.normalize_full_df(ml_df)
        ml_df.to_csv(ROOT_PATH + "/Modeling/{}_ml.csv".format(self.league.lower()), index=False)
        return ml_df

    def run_target(self):  # Run
        target_cols = ["ESPN_ID", "datetime", "Final_Status",
                       "Home_Score_x", "Away_Score_x", "Line", "Over_Under", "HQ1_x", "HQ2_x", "HQ3_x", "HQ4_x", "HOT",
                       "AQ1_x", "AQ2_x", "AQ3_x", "AQ4_x", "AOT", "Home_ML", "Away_ML", "Open_OU", "Close_OU", "2H_OU",
                       "Open_Home_Line", "Open_Away_Line", "Close_Home_Line", "Close_Away_Line", "2H_Home_Line", "2H_Away_Line",
                       "Over_ESB", "Over_ml_ESB", "Under_ESB", "Under_ml_ESB", "Home_Line_ESB", "Home_Line_ml_ESB",
                       "Away_Line_ESB", "Away_Line_ml_ESB", "Home_ML_ESB", "Away_ML_ESB"
                       ]
        prod_df = self.load_prod_df()
        target_df = prod_df.loc[:, target_cols]
        target_df.to_csv(ROOT_PATH + "/Modeling/{}_target.csv".format(self.league.lower()), index=False)
        return target_df

    def update_finished_game(self):  # Run  TODO
        """
        loads the current ml df, finds games that are not finished,
        checks if they are now finished, and updates the row if it is
        - easy way of updating the ml_df with newly finished games without
          recreating the entire table each time
        """
        pass


if __name__ == "__main__":
    x = Prod_to_ML("NBA")
    self = x
    # df = x.run(normalize=False)
