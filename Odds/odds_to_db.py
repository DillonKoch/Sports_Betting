# ==============================================================================
# File: odds_to_db.py
# Project: Odds
# File Created: Sunday, 23rd August 2020 2:25:37 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 29th August 2020 4:12:19 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for cleaning odds data and inserting it into the sqlite database
# ==============================================================================


import datetime
import json
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm


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
        self.Is_neutral = None

        # quarter/half scores
        self.Home_1Q = None
        self.Home_2Q = None
        self.Home_3Q = None
        self.Home_4Q = None
        self.Home_1H = None
        self.Home_2H = None
        self.Home_OT = None
        self.Home_Final = None
        self.Away_1Q = None
        self.Away_2Q = None
        self.Away_3Q = None
        self.Away_4Q = None
        self.Away_1H = None
        self.Away_2H = None
        self.Away_OT = None
        self.Away_Final = None

        # betting info
        self.OU_Open = None
        self.OU_Close = None
        self.OU_2H = None
        self.Home_Spread_Open = None
        self.Home_Spread_Close = None
        self.Home_Spread_2H = None
        self.Away_Spread_Open = None
        self.Away_Spread_Close = None
        self.Away_Spread_2H = None
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
        row = [self.Season, self.Date, self.Home, self.Away,
               self.Home_1Q, self.Home_2Q, self.Home_3Q, self.Home_4Q,
               self.Home_1H, self.Home_2H, self.Home_OT, self.Home_Final,
               self.Away_1Q, self.Away_2Q, self.Away_3Q, self.Away_4Q,
               self.Away_1H, self.Away_2H, self.Away_OT, self.Away_Final,
               self.OU_Open, self.OU_Close, self.OU_2H,
               self.Home_Spread_Open, self.Home_Spread_Close, self.Home_Spread_2H,
               self.Away_Spread_Open, self.Away_Spread_Close, self.Away_Spread_2H,
               self.Home_ML, self.Away_ML]
        return row

    def calculate_overtimes(self, league):
        if league == "NCAAB":
            self.Home_OT = self.Home_Final - sum([self.Home_1H, self.Home_2H])
            self.Away_OT = self.Away_Final - sum([self.Away_1H, self.Away_2H])
        else:
            self.Home_OT = self.Home_Final - sum([self.Home_1Q, self.Home_2Q, self.Home_3Q, self.Home_4Q])
            self.Away_OT = self.Away_Final - sum([self.Away_1Q, self.Away_2Q, self.Away_3Q, self.Away_4Q])


class Odds_to_db:
    """
    class to convert raw odds data downloaded (with Season col added) to
    a cleaner dataframe with one row per game, then insert to database
    """

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
        loads all the individual season odds df's, merges them and resets index
        """
        df_paths = listdir_fullpath(ROOT_PATH + "/Odds/{}/".format(self.league))
        df_paths = [path for path in df_paths if ".csv" in path]
        dfs = [pd.read_csv(df_path) for df_path in df_paths]
        full_df = pd.concat(dfs)
        full_df.reset_index(inplace=True, drop=True)
        return full_df

    def clean_odds_data(self, odds_df):  # Top Level
        """
        - some values are like 13-109 if there's a different moneyline, so just taking the spread
        - replacing "pk" and "PK" with 0 or 100 (for moneyline)
        - filling null with "NL" and replacing "NL" with np.nan
        - finally making all odds columns floats
        """
        for col in ["Open", "Close", "2H"]:
            for i, item in enumerate(list(odds_df[col])):
                try:
                    _ = float(item)
                except BaseException:
                    if '-' in str(item):
                        odds_df.loc[i, col] = item.split('-')[0]

        for val in ["PK", "pk"]:
            odds_df['Open'].replace(val, 0.0, inplace=True)
            odds_df['Close'].replace(val, 0.0, inplace=True)
            odds_df['ML'].replace(val, 100, inplace=True)
            odds_df['2H'].replace(val, 0.0, inplace=True)

        for col in ["Open", "Close", "ML", "2H"]:
            odds_df[col].fillna(value="NL", inplace=True)
            odds_df[col].replace("NL", np.nan, inplace=True)
            odds_df[col] = odds_df[col].astype(float)

        return odds_df

    def apply_team_conversions(self, df):  # Top Level
        """
        converts the original odds team names to the ESPN names
        """
        for key, value in list(self.conversions_dict.items()):
            if value == "":
                value = key
            print(f"{key} --> {value}")
            df = df.replace(key, self.conversions_dict[key])
        print('\n\n\n')
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

    def create_new_df(self):  # Top Level
        """
        initializes final df for odds data in all leagues
        - NCAAB will have no values for 1-4Q
        - Other leagues will have no value for 1-2H
        """

        cols = ["Season", "datetime", "Home", "Away",
                "H1Q", "H2Q", "H3Q", "H4Q",
                "H1H", "H2H", "HOT", "HFinal",
                "A1Q", "A2Q", "A3Q", "A4Q",
                "A1A", "A2A", "AOT", "AFinal",
                "OU_Open", "OU_Close", "OU_2H",
                "Home_Spread_Open", "Home_Spread_Close", "Home_Spread_2H",
                "Away_Spread_Open", "Away_Spread_Close", "Away_Spread_2H",
                "Home_ML", "Away_ML"]

        return pd.DataFrame(columns=cols)

    def _ensure_games_match(self, row_1, row_2):  # QA Testing
        """
        tests to be sure that the two rows are for the same game
        """
        assert row_1['Date'] == row_2['Date']
        assert row_1['Season'] == row_2['Season']

        # ensures visitor/home values are either "neutral" or "home"/"visitor"
        vh_combo = [row_1['VH'], row_2['VH']]
        assert (vh_combo[0] != vh_combo[1]) or (vh_combo[0] == 'N' and vh_combo[1] == 'N')

    def _add_home_away(self, odds_game, home_row, away_row):  # Helping Helper _create_odds_game
        """
        adds team names to the odds_game object
        """
        odds_game.Home = home_row['Team']
        odds_game.Away = away_row['Team']
        return odds_game

    def _add_date(self, odds_game, home_row):  # Helping Helper _create_odds_game
        """
        cleans the date from home_row to datetime to add to odds_game
        """
        year = home_row['year']

        date_str = str(home_row['Date'])
        month = date_str[:2] if len(date_str) == 4 else date_str[0]
        day = date_str[2:] if len(date_str) == 4 else date_str[1:]

        dt = datetime.date(int(year), int(month), int(day))
        odds_game.Date = dt
        return odds_game

    def _add_scores(self, odds_game, home_row, away_row):  # Helping Helper _create_odds_game
        """
        adding scores from the two rows to odds_game
        """
        if self.league != "NCAAB":
            odds_game.Home_1Q = home_row['1st']
            odds_game.Home_2Q = home_row['2nd']
            odds_game.Home_3Q = home_row['3rd']
            odds_game.Home_4Q = home_row['4th']
            odds_game.Away_1Q = away_row['1st']
            odds_game.Away_2Q = away_row['2nd']
            odds_game.Away_3Q = away_row['3rd']
            odds_game.Away_4Q = away_row['4th']
        else:
            odds_game.Home_1H = home_row['1st']
            odds_game.Home_2H = home_row['2nd']
            odds_game.Away_1H = away_row['1st']
            odds_game.Away_2H = away_row['2nd']

        odds_game.Home_Final = home_row['Final']
        odds_game.Away_Final = away_row['Final']

        odds_game.calculate_overtimes(league=self.league)
        return odds_game

    def _add_moneylines(self, odds_game, home_row, away_row):  # Helping Helper _create_odds_game
        """
        adding moneylines to odds_game
        """
        odds_game.Home_ML = home_row['ML']
        odds_game.Away_ML = away_row['ML']
        return odds_game

    def _get_spread_ou(self, home_row, away_row, column):  # Helping Helper _create_odds_game
        """
        given the home and away row, this method returns the over under and home/away spreads
        - works for Open/Close/2H columns (pass which one to column argument)
        """
        spread_ou_vals = [home_row[column], away_row[column]]
        spread_val, ou_val = sorted(spread_ou_vals)  # spread val always < over under val
        home_spread = spread_val * -1 if home_row[column] == spread_val else spread_val
        away_spread = spread_val * -1 if away_row[column] == spread_val else spread_val
        return ou_val, home_spread, away_spread

    def _create_odds_game(self, row_1, row_2):  # Specific Helper populate_new_df
        """
        given two rows from odds df, this method creates a new ESB_Game object
        including all the info from the two odds df rows
        """
        self._ensure_games_match(row_1, row_2)

        # home_row/away_row used in methods that need to know which row is home
        home_row = row_1 if row_1['VH'] in ["N", "H"] else row_2
        away_row = row_1 if row_1['VH'] not in ["N", "H"] else row_2

        # creating game object and initial info
        odds_game = Odds_Game()
        odds_game.Season = home_row['Season']  # already confirmed seasons match
        odds_game.Is_neutral = True if home_row['VH'] == "N" else False

        # modifying odds_game object with helper methods
        odds_game = self._add_home_away(odds_game, home_row, away_row)
        odds_game = self._add_date(odds_game, home_row)  # already confirmed dates match
        odds_game = self._add_scores(odds_game, home_row, away_row)
        odds_game = self._add_moneylines(odds_game, home_row, away_row)

        # open home/away spread and over under
        open_ou, open_home_spread, open_away_spread = self._get_spread_ou(home_row, away_row, "Open")
        odds_game.OU_Open = open_ou
        odds_game.Home_Spread_Open = open_home_spread
        odds_game.Away_Spread_Open = open_away_spread

        # close home/away spread and over under
        close_ou, close_home_spread, close_away_spread = self._get_spread_ou(home_row, away_row, "Close")
        odds_game.OU_Close = close_ou
        odds_game.Home_Spread_Close = close_home_spread
        odds_game.Away_Spread_Close = close_away_spread

        # second half home/away spread and over under
        ou_2h, home_spread_2h, away_spread_2h = self._get_spread_ou(home_row, away_row, "2H")
        odds_game.OU_2H = ou_2h
        odds_game.Home_Spread_2H = home_spread_2h
        odds_game.Away_Spread_2H = away_spread_2h

        return odds_game

    def populate_new_df(self, odds_df, new_df):  # Top Level
        """
        iterates through rows of the whole odds df to create a new, cleaner df with one row per game
        - as it iterates, it finds the first game and saves it in game_1, then once it has
          game_2 in the next iteration, both game rows are passed to create_esb_game to
          get back a clean row for new_df
        """
        for i in tqdm(range(len(odds_df))):
            if i % 2 == 0:
                row_1 = odds_df.iloc[i, :]
            else:
                row_2 = odds_df.iloc[i, :]
                odds_game = self._create_odds_game(row_1, row_2)
                new_df.loc[len(new_df)] = odds_game.to_row()
        return new_df

    def sort_df(self, new_df):  # Top Level
        """
        sorts the new_df by datetime once each row contains a full game
        """
        new_df['datetime'] = pd.to_datetime(new_df['datetime'])
        new_df.sort_values(by='datetime', inplace=True)
        return new_df

    def run(self):  # Run
        odds_df = self.load_odds_data()
        odds_df = self.clean_odds_data(odds_df)
        odds_df = self.apply_team_conversions(odds_df)
        if self.league in ["NFL", "NBA"]:
            self.assert_teams_valid(odds_df)
        new_df = self.create_new_df()
        new_df = self.populate_new_df(odds_df, new_df)
        new_df = self.sort_df(new_df)

        # save to database
        s = Sqlite_util()
        s.insert_df(new_df, f"{self.league}_Odds")
        return odds_df, new_df


if __name__ == "__main__":
    x = Odds_to_db("NFL")
    self = x
    odds_df, new_df = x.run()
