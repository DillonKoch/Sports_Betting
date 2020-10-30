# ==============================================================================
# File: merge_league_data.py
# Project: Odds
# File Created: Sunday, 25th October 2020 1:20:02 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 29th October 2020 8:41:24 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Merges all the individual season .csv's in each league to one clean df
# ==============================================================================


import datetime
import os
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


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

    def calculate_overtimes(self, league):  # Top Level
        if league == "NCAAB":
            self.Home_OT = self.Home_Final - sum([self.Home_1H, self.Home_2H])
            self.Away_OT = self.Away_Final - sum([self.Away_1H, self.Away_2H])
        else:
            self.Home_OT = self.Home_Final - sum([self.Home_1Q, self.Home_2Q, self.Home_3Q, self.Home_4Q])
            self.Away_OT = self.Away_Final - sum([self.Away_1Q, self.Away_2Q, self.Away_3Q, self.Away_4Q])

    def to_row(self):  # Run
        """
        converts the object to a list to be inserted to an odds df
        """
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


class Merge_League_Data:
    def __init__(self):
        pass

    def load_data(self, league):  # Top Level  Tested
        """
        loads all the individual season odds df's, merges them and resets index
        """
        df_paths = listdir_fullpath(ROOT_PATH + f"/Odds/{league}")
        df_paths = [df_path for df_path in df_paths if '.csv' in df_path]
        dfs = [pd.read_csv(df_path) for df_path in df_paths]
        full_df = pd.concat(dfs)
        full_df.reset_index(inplace=True, drop=True)
        return full_df

    def _clean_pks(self, df):  # Specific Helper clean_data  Tested
        """
        replaces 'pickem' values with 0 for spread and 100 for ML
        """
        for val in ["PK", "pk"]:
            df['Open'].replace(val, 0.0, inplace=True)
            df['Close'].replace(val, 0.0, inplace=True)
            df['ML'].replace(val, 100, inplace=True)
            df['2H'].replace(val, 0.0, inplace=True)
        return df

    def _clean_spread_mls(self, df):  # Specific Helper clean_data  Tested
        """
        sometimes the spread has a moneyline attached if it's not -110 (3.5-109)
        - this will get rid of the moneyline part and just return the spread
        """
        for col in ["Open", "Close", "2H"]:
            for i, item in enumerate(list(df[col])):
                try:
                    _ = float(item)
                except BaseException:
                    if '-' in str(item):
                        df.loc[i, col] = item.split('-')[0]
        return df

    def _clean_no_lines(self, df):  # Specific Helper clean_data  Tested
        """
        replacing "NL" values with np.nan
        """
        for col in ["Open", "Close", "ML", "2H"]:
            df[col].fillna(value="NL", inplace=True)
            df[col].replace("NL", np.nan, inplace=True)
        return df

    def clean_data(self, df):  # Top Level  Tested
        df = df.replace("24,5", 24.5)  # TODO remove in 2021
        df = self._clean_spread_mls(df)
        df = self._clean_pks(df)
        df = self._clean_no_lines(df)
        for col in ["Open", "Close", "ML", "2H"]:
            df[col] = df[col].astype(float)

        return df

    def create_df(self):  # Top Level  Tested
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

    def _ensure_games_match(self, row_1, row_2):  # QA Testing _create_odds_game
        """
        tests to be sure that the two rows are for the same game
        """
        try:
            assert row_1['Date'] == row_2['Date']
            assert row_1['Season'] == row_2['Season']
            assert row_1['datetime'] == row_2['datetime']
        except BaseException:
            print(row_1, row_2)

        # ensures visitor/home values are either "neutral" or "home"/"visitor"
        vh_combo = [row_1['VH'], row_2['VH']]
        assert (vh_combo[0] != vh_combo[1]) or (vh_combo[0] == 'N' and vh_combo[1] == 'N')

    def _add_one_liners(self, odds_game, home_row, away_row):  # Helping Helper _create_odds_game  Tested
        """
        adds team names to the odds_game object
        """
        odds_game.Home = home_row['Team']
        odds_game.Away = away_row['Team']
        odds_game.Date = home_row['datetime']
        odds_game.Home_ML = home_row['ML']
        odds_game.Away_ML = away_row['ML']
        return odds_game

    def _add_scores(self, odds_game, home_row, away_row, league):  # Helping Helper _create_odds_game  Tested
        """
        adding scores from the two rows to odds_game
        """
        if league != "NCAAB":
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

        odds_game.calculate_overtimes(league=league)
        return odds_game

    def _get_spread_ou(self, home_row, away_row, column, league):  # Helping Helper _create_odds_game
        """
        given the home and away row, this method returns the over under and home/away spreads
        - works for Open/Close/2H columns (pass which one to column argument)
        """
        spread_ou_vals = [home_row[column], away_row[column]]
        print(spread_ou_vals)
        # spread_val, ou_val = sorted(spread_ou_vals)  # spread val always < over under val

        # if np.nan not in spread_ou_vals:
        if sum([np.isnan(item) for item in spread_ou_vals]) < 0:
            spread_val, ou_val = sorted(spread_ou_vals)
            print('didnt get to else')
        else:
            print('here')
            non_nl = [i for i in spread_ou_vals if not np.isnan(i)][0]
            print(non_nl)
            if league in ['NFL', 'NCAAF']:
                spread_val = non_nl if non_nl < 15 else np.nan
                ou_val = non_nl if spread_val == np.nan else np.nan
            else:
                spread_val = non_nl if non_nl < 30 else np.nan
                ou_val = non_nl if spread_val == np.nan else np.nan

        home_spread = spread_val * -1 if home_row[column] == spread_val else spread_val
        away_spread = spread_val * -1 if away_row[column] == spread_val else spread_val
        return ou_val, home_spread, away_spread

    def _create_odds_game(self, row_1, row_2, league):  # Specific Helper populate_df
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
        odds_game = self._add_one_liners(odds_game, home_row, away_row)
        odds_game = self._add_scores(odds_game, home_row, away_row, league)
        odds_game = self._add_moneylines(odds_game, home_row, away_row)

    def populate_df(self, odds_df, new_df, league):  # Top Level
        """
        iterates through rows of the whole odds df to create a new, cleaner df with one row per game
        - as it iterates, it finds the first row for a game and saves it in row_1, then once it has
          row_2 in the next iteration, both rows are passed to create_esb_game to
          get back a clean row for new_df
        """
        for i in tqdm(range(len(odds_df))):
            if i % 2 == 0:
                row_1 = odds_df.iloc[i, :]
            else:
                row_2 = odds_df.iloc[i, :]
                odds_game = self._create_odds_game(row_1, row_2, league)
                # new_df.loc[len(new_df)] = odds_game.to_row()
        return new_df

    def run(self, league):  # Run
        # * load odds data - load/merge individual csv's
        # * clean odds data - cleaning values
        # ? apply team name conversions using json conversion file
        # ? assert team names are valid (NFL/NBA atm)
        # * create new df (will be the final df)
        # * populate new df with the merged df of all individual seasons
        # * sort the df
        odds_df = self.load_data(league)
        odds_df = self.clean_data(odds_df)
        new_df = self.create_df()
        # new_df = self.populate_df(odds_df, new_df)
        return new_df


if __name__ == '__main__':
    x = Merge_League_Data()
    self = x
    league = 'NFL'
    val_dic = {"NFL": [], "NBA": [], "NCAAF": [], "NCAAB": []}
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        print(league)
        df = x.load_data(league)
        row_pairs = []

        for i in range(min(100, len(df))):
            if i % 2 == 0:
                row_1 = df.iloc[i, :]
            else:
                row_2 = df.iloc[i, :]
                row_pairs.append([row_1, row_2])

        for pair in row_pairs:
            row1, row2 = pair
            for col in ['Open', 'Close', '2H']:
                vals = [row1[col], row2[col]]
                if vals.count("NL") == 1:
                    val_dic[league].append(vals)

        # new_df = x.run(league)
