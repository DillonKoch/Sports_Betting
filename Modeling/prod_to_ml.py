# ==============================================================================
# File: prod_to_ml.py
# Project: Modeling
# File Created: Tuesday, 14th July 2020 4:47:07 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 15th July 2020 8:43:19 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Agent for converting a row from a PROD df to ML-usable data
# (this is replacing the former method of using dictionaries and df.iterrows()
# for updating the records and average team stats)
# ==============================================================================


import sys
from os.path import abspath, dirname
import json


import datetime
import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN_Scrapers.team_stats_scraper import Team_Stats


class Prod_to_ML:
    def __init__(self, league: str):
        self.league = league
        self.football_league = True if self.league in ["NFL", "NCAAB"] else False

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

    def _replace_relocated_teams(self, df):  # Specific Helper load_prod_df
        df = df.replace("San Diego Chargers", "Los Angeles Chargers")
        df = df.replace("Oakland Raiders", "Las Vegas Raiders")
        df = df.replace("St. Louis Rams", "Los Angeles Rams")
        return df

    def _add_prod_cols(self, prod_df):  # Specific Helper load_prod_df
        """
        loads the league's PROD df and adds conference and neutral T/F columns
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

    def _clean_stats_cols(self, df):
        # remove the current dash cols, insert d1/d2 cols

        for col in self.dash_cols:
            df[col] = df[col].fillna("0-0")

        new_dash_cols = ["{}_d1".format(col) if i % 2 == 0 else "{}_d2".format(col)
                         for col in self.dash_cols for i in range(2)]
        for col in new_dash_cols:
            df[col] = None

        def expand_row(row):
            for col in self.dash_cols:
                val1, val2 = row[col].split('-')
                row["{}_d1".format(col)] = int(val1)
                row["{}_d2".format(col)] = int(val2)
            return row
        df = df.apply(lambda row: expand_row(row), axis=1)
        return df

    def load_prod_df(self):  # Top Level
        df = pd.read_csv(ROOT_PATH + "/PROD/{}_PROD.csv".format(self.league.upper()))
        df = self._replace_relocated_teams(df)
        df = self._add_prod_cols(df)
        df = self._clean_stats_cols(df)
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

    def _get_home_record(self, df):  # Specific Helper get_record
        results = list(df['Home_won'])
        wins = results.count(True)
        losses = results.count(False)
        ties = list(df['tie']).count(True)
        return wins, losses, ties

    def _get_away_record(self, df):  # Specific Helper get_record
        results = list(df['Home_won'])
        wins = results.count(False)
        losses = results.count(True)
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
        home_wins, home_losses, home_ties = self._get_home_record(home_df)

        away_df = df.loc[(df.Away == team_name) & (df.neutral_game == False)]
        away_wins, away_losses, away_ties = self._get_away_record(away_df)

        home_neutral_df = df.loc[(df.Home == team_name) & (df.neutral_game == True)]
        home_neutral_wins, home_neutral_losses, home_neutral_ties = self._get_home_record(home_neutral_df)

        away_neutral_df = df.loc[(df.Away == team_name) & (df.neutral_game == True)]
        away_neutral_wins, away_neutral_losses, away_neutral_ties = self._get_away_record(away_neutral_df)

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

    def add_records(self, df, prod_df):  # Top Level
        cols = ["ovr_wins", "ovr_losses", "ovr_ties", "spec_wins", "spec_losses", "spec_ties"]
        home_cols = ["home_" + item for item in cols]
        away_cols = ["away_" + item for item in cols]
        all_record_cols = home_cols + away_cols

        def add_records(row, all_record_cols):
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

        prod_df = prod_df.apply(lambda row: add_records(row, all_record_cols), axis=1)
        record_df = prod_df.loc[:, all_record_cols]
        df = pd.concat([df, record_df])
        return df

    def _specific_stats(self, df):  # Specific Helper get_team_stats
        pass

    def get_team_stats(self, df, team_name: str):
        """
        returns the avg stats values for a team from the dataframe input
        - format: overall avg_stats_cols, spec_avg_stats_cols (just like record)
        - football: x cols
        - basketball: x cols
        """
        home_df = df.loc[(df.Home == team_name) & (df.neutral_game == False)]
        home_stats = self._specific_stats(home_df)

        away_df = df.loc[(df.Away == team_name) & (df.neutral_game == False)]

        home_neutral_df = df.loc[(df.Home == team_name) & (df.neutral_game == True)]

        away_neutral_df = df.loc[(df.Away == team_name) & (df.neutral_game == True)]
    
    def add_team_stats(self, df, prod_df):  # Top Level
        # make this similar to adding records!
        pass

    def add_dummies(self, df, prod_df):  # Top Level
        dummy_cols = ["Home", "Away", "Network"]
        for col in dummy_cols:
            new_dummy_df = pd.get_dummies(prod_df[col], prefix=col)
            df = pd.concat([df, new_dummy_df], axis=1)
        return df

    def add_binary_cols(self, df, prod_df):  # Top Level
        df['neutral_game'] = prod_df['neutral_game'].astype(int)
        df['conf_game'] = prod_df['conf_game'].astype(int)
        return df

    def add_season(self, df, prod_df):  # Top Level
        df['Season'] = prod_df['Season_x'].astype(int)
        return df

    def add_week(self, df, prod_df):  # Top Level
        if self.league != "NFL":
            return df

        prod_weeks = list(prod_df['Week'])
        prod_weeks = [item.replace("WC", '18').replace("DIV", "19").replace("CONF", "20").replace("SB", "21")
                      for item in prod_weeks]
        df['Week'] = pd.Series(prod_weeks).astype(int)
        return df

    def get_training_data(self):  # Run
        prod_df = self.load_prod_df()
        prod_df = prod_df.loc[prod_df.Final_Status.notnull()]

        df = pd.DataFrame()
        df = self.add_dummies(df, prod_df)
        df = self.add_binary_cols(df, prod_df)
        df = self.add_season(df, prod_df)
        df = self.add_week(df, prod_df)
        df = self.add_records(df, prod_df)
        # take the prod df, make a new df with records/stats, append horizontally
        return df

    def get_game_vector(self, ESPN_ID):  # Run
        # vector for one game, used for predicting
        pass


if __name__ == "__main__":
    x = Prod_to_ML("NFL")
    self = x
    prod_df = x.load_prod_df()
    # min_df = x.get_team_info(prod_df, "Minnesota Vikings", 2009, datetime.date.today(), home=True)
    # df = self.get_training_data()
