# ==============================================================================
# File: odds_to_db.py
# Project: Odds
# File Created: Sunday, 23rd August 2020 2:25:37 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 23rd August 2020 8:46:16 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for cleaning odds data and inserting it into the sqlite database
# ==============================================================================


import json
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.sqlite_util import Sqlite_util
from Utility.Utility import listdir_fullpath


class Odds_Game:
    """
    class to represent a game from the Odds files
    - games were originally represented in two rows, this helps
      convert them into one row per game
    """

    def __init__(self):
        # general info
        self.Home = None
        self.Away = None
        self.Date = None
        self.Season = None

        # quarter/half scores
        self.Home_1Q = None
        self.Home_2Q = None
        self.Home_3Q = None
        self.Home_4Q = None
        self.Home_1H = None
        self.Home_2H = None
        self.Home_Final = None
        self.Away_1Q = None
        self.Away_2Q = None
        self.Away_3Q = None
        self.Away_4Q = None
        self.Away_1H = None
        self.Away_2H = None
        self.Away_Final = None

        # betting info
        self.OU_Open = None
        self.OU_Close = None
        self.OU_2H = None
        self.Home_Spread_Open = None
        self.Home_Spread_Close = None
        self.Home_Spread_2H = None
        self.Home_ML = None
        self.Away_ML = None

    def _date_to_dt(self):  # Specific Helper to_row
        if isinstance(self.Date, str):
            pass

    def to_row(self):  # Run
        """
        converts the object to a list to be inserted to an odds df
        """
        self._date_to_dt()
        row = [self.Date, self.Season, self.Home, self.Away,
               self.Home_1Q, self.Home_2Q, self.Home_3Q, self.Home_4Q,
               self.Home_1H, self.Home_2H, self.Home_Final,
               self.Away_1Q, self.Away_2Q, self.Away_3Q, self.Away_4Q,
               self.Away_1H, self.Away_2H, self.Away_Final,
               self.OU_Open, self.OU_Close, self.OU_2H,
               self.Home_Spread_Open, self.Home_Spread_Close, self.Home_Spread_2H,
               self.Home_ML, self.Away_ML]
        return row


class Odds_to_db:
    def __init__(self, league):
        self.league = league

    @property
    def df_cols(self):  # Property
        """
        returns the expected df columns for a df downloaded from the website
        - needs "Season" to be added to the raw df
        - differs for NCAAB because they play 2 halves
        """
        if self.league == "NCAAB":
            cols = []  # FIXME
        else:
            cols = ['Season', 'Date', 'Rot', 'VH', 'Team', '1st', '2nd',
                    '3rd', '4th', 'Final', 'Open', 'Close', 'ML', '2H']
        return cols

    @property
    def current_teams(self):  # Property
        """
        returns the current teams in the league, provided by Utility/current_teams.json
        """
        with open(ROOT_PATH + "/Utility/current_teams.json") as f:
            teams_dict = json.load(f)
        teams = teams_dict[self.league]
        return teams

    @property
    def conversions_dict(self):  # Property
        """
        returns a dict to convert odds team names to the ESPN team names
        """
        with open(ROOT_PATH + "/Odds/team_conversions.json") as f:
            dic = json.load(f)
        return dic[self.league]

    def load_odds_data(self):  # Top Level
        """
        loads all the individual season odds df's, merges them and sorts by season/date
        """
        df_paths = listdir_fullpath(ROOT_PATH + "/Odds/{}/".format(self.league))
        df_paths = [path for path in df_paths if ".csv" in path]
        dfs = [pd.read_csv(df_path) for df_path in df_paths]
        full_df = pd.concat(dfs)
        return full_df

    def apply_team_conversions(self, df):  # Top Level
        """
        converts the original odds team names to the ESPN names
        """
        for key, value in list(self.conversions_dict.items()):
            print(f"{key} --> {value}")
            df = df.replace(key, self.conversions_dict[key])
        return df

    def assert_teams_valid(self, df):  # QA Testing
        """
        ensures all the teams in the odds df are current team names from ESPN
        """
        teams = list(df.Team)
        teams = list(set(teams))
        for team in teams:
            assert team in self.current_teams, f"Team '{team}' is not in current teams!"
        print("all team names valid!")

    def combine_game_rows(self, df):  # Top Level
        for i, row in df.iterrows():
            pass

        return df

    def run(self):  # Run
        df = self.load_odds_data()
        df = self.apply_team_conversions(df)
        self.assert_teams_valid(df)
        # clean the df
        s = Sqlite_util()
        s.insert_df(df, f"{self.league}_Odds")
        return df


if __name__ == "__main__":
    x = Odds_to_db("NBA")
    self = x
    df = x.run()
