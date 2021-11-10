# ==============================================================================
# File: clean_sbo.py
# Project: allison
# File Created: Sunday, 15th August 2021 7:56:23 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 15th August 2021 7:56:24 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# cleaning data from /Data/Odds/ into one csv file per league, with one game per row
# ==============================================================================


import concurrent.futures
import datetime
import json
import os
import re
import sys
import warnings
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


warnings.filterwarnings("ignore")


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def multithread(func, func_args):  # Multithreading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = list(tqdm(executor.map(func, func_args), total=len(func_args)))
    return result


class SBO_Clean_Data:
    def __init__(self, league):
        self.league = league
        self.df_cols = ['Season', 'Date', 'Home', 'Away', 'Is_Neutral',
                        'OU_Open', 'OU_Open_ML', 'OU_Close', 'OU_Close_ML', 'OU_2H', 'OU_2H_ML',
                        'Home_Line_Open', 'Home_Line_Open_ML', 'Away_Line_Open', 'Away_Line_Open_ML',
                        'Home_Line_Close', 'Home_Line_Close_ML', 'Away_Line_Close', 'Away_Line_Close_ML',
                        'Home_Line_2H', 'Home_Line_2H_ML', 'Away_Line_2H', 'Away_Line_2H_ML',
                        'Home_ML', 'Away_ML']
        self.team_dict = self.load_team_dict()

    def load_team_dict(self):  # Top Level
        """
        loads dict with all the official team info from ESPN
        """
        path = ROOT_PATH + f"/Data/Teams/{self.league}_Teams.json"
        with open(path) as f:
            team_dict = json.load(f)
        return team_dict

    def odds_path_to_season(self, odds_path):  # Top Level
        """
        finds the season string inside the odds df path (like 2020-21)
        """
        filename = odds_path.split('/')[-1]
        season = re.findall(re.compile(r"\d{4}-\d{2}"), filename)[0]
        return season

    def odds_df_to_row_pairs(self, odds_df):  # Top Level
        """
        converts the odds dataframe into a list of row pairs, since each game has 2 rows in the df
        """
        row_lists = odds_df.values.tolist()
        row_pairs = [(row_lists[i], row_lists[i + 1]) for i in range(0, len(row_lists), 2)]
        return row_pairs

    def check_game_in_january(self, row_pair):  # Top Level
        """
        returns True if the game is in January, else False
        - used to change the year over in the date (change as soon as we see January)
        """
        row1, _ = row_pair
        date1 = str(row1[0])
        return True if (len(date1) == 3) and (date1[0] == '1') else False

    def _date(self, row_pair, season, seen_january):  # Specific Helper row_pair_to_df
        """
        uses the row_pair to create a datetime object of the game date
        """
        row1, row2 = row_pair
        date1 = str(row1[0])
        date2 = str(row2[0])
        assert date1 == date2

        year = int(season[:4]) + 1 if seen_january else int(season[:4])
        month = date1[:2] if len(date1) == 4 else date1[0]
        day = date1[-2:]
        dt_ob = datetime.datetime(year, int(month), int(day))
        return dt_ob.strftime("%Y-%m-%d")

    def _home_away_row(self, row_pair):  # Global Helper
        """
        given a row pair, this method identifies the home and away row specifically
        """
        row1, row2 = row_pair
        row1_vh = row1[2]
        row2_vh = row2[2]
        assert [row1_vh, row2_vh] in [['V', 'H'], ['H', 'V'], ['N', 'N']]
        row1_home = row1_vh in ['H', 'N']
        home_row = row1 if row1_home else row2
        away_row = row2 if row1_home else row1
        return home_row, away_row

    def _find_team_name(self, name):  # Helping Helper _home_away_neutral
        """
        finds the official ESPN team name for the scraped name
        - if the name has no official name and isn't in 'Other Names', this raises an error
        """
        official_names = list(self.team_dict['Teams'].keys())
        if name in official_names:
            return name

        for official_name in official_names:
            if name in self.team_dict['Teams'][official_name]['Other Names']:
                return official_name

        if name not in self.team_dict['Other Teams']:
            raise ValueError("COULD NOT FIND OFFICIAL TEAM NAME")
        return name

    def _home_away_neutral(self, row_pair):  # Specific Helper row_pair_to_df
        """
        returns the home/away official name from the row pair, and whether the game is at a neutral location
        """
        home_row, away_row = self._home_away_row(row_pair)
        home = self._find_team_name(home_row[3])
        away = self._find_team_name(away_row[3])
        is_neutral = 1 if home_row[2] == 'N' else 0
        return home, away, is_neutral

    def _bet_val_to_val_ml(self, bet_val):  # Helping Helper _open_close_2h_bets
        """
        converts the bet_val from the odds df into either the val, None or the val, ML
        - ML only shows up when the bet_val is in format 7-105
        """
        try:
            bet_val = str(bet_val).lower().replace('pk', '0')
            if '-' in bet_val:
                val, ml_val = bet_val.split('-')
                ml_val = -float(ml_val)
            else:
                val = bet_val
                ml_val = -110
            return float(val), float(ml_val)
        except Exception as e:
            print(e)
            print(bet_val)

    def _open_close_2h_bets(self, row_pair, col_index):  # Specific Helper row_pair_to_df
        """
        given a row pair and col index, this method returns the O/U, lines for open/close/2h
        """
        # * returning None's if the line is "NL"
        home_row, away_row = self._home_away_row(row_pair)
        if 'nl' in [str(home_row[col_index]).lower(), str(away_row[col_index]).lower()]:
            return None, None, None, None, None, None

        # * extracting home/away values and ML values, determining if home is over/under or not
        home_val, home_ml_val = self._bet_val_to_val_ml(home_row[col_index])
        away_val, away_ml_val = self._bet_val_to_val_ml(away_row[col_index])
        home_is_ou = home_val > away_val

        # * setting O/U, home/away lines based on data from rows
        ou = home_val if home_is_ou else away_val
        ou_ml = home_ml_val if home_is_ou else away_ml_val
        hline = away_val if home_is_ou else (-1 * home_val)
        hline_ml = (-220 - away_ml_val) if home_is_ou else home_ml_val
        aline = (-1 * away_val) if home_is_ou else home_val
        aline_ml = away_ml_val if home_is_ou else (-220 - home_ml_val)
        return ou, ou_ml, hline, hline_ml, aline, aline_ml

    def _ml_bets(self, row_pair):  # Specific Helper row_pair_to_df
        """
        finding the ML bets in the row_pair
        """
        home_row, away_row = self._home_away_row(row_pair)
        if 'nl' in [str(home_row[-2]).lower(), str(away_row[-2]).lower()]:
            return None, None
        home_ml = float(str(home_row[-2]).lower().replace('pk', '0'))
        away_ml = float(str(away_row[-2]).lower().replace('pk', '0'))
        return home_ml, away_ml

    def row_pair_to_df(self, row_pair, df, season, seen_january):  # Top Level
        """
        adding data from the row pair (one game) to the df
        """
        # date, rot, vh, team, 1st, 2nd, 3rd, 4th, final, open, close, ml, 2h
        date = self._date(row_pair, season, seen_january)
        home, away, is_neutral = self._home_away_neutral(row_pair)
        ou_open, ou_open_ml, hline_open, hline_open_ml, aline_open, aline_open_ml = self._open_close_2h_bets(row_pair, -4)
        ou_close, ou_close_ml, hline_close, hline_close_ml, aline_close, aline_close_ml = self._open_close_2h_bets(row_pair, -3)
        ou_2h, ou_2h_ml, hline_2h, hline_2h_ml, aline_2h, aline_2h_ml = self._open_close_2h_bets(row_pair, -1)
        home_ml, away_ml = self._ml_bets(row_pair)
        new_row = [season, date, home, away, is_neutral,
                   ou_open, ou_open_ml, ou_close, ou_close_ml, ou_2h, ou_2h_ml,
                   hline_open, hline_open_ml, aline_open, aline_open_ml,
                   hline_close, hline_close_ml, aline_close, aline_close_ml,
                   hline_2h, hline_2h_ml, aline_2h, aline_2h_ml,
                   home_ml, away_ml]
        df.loc[len(df)] = new_row
        return df

    def run(self):  # Run
        df = pd.DataFrame(columns=self.df_cols)
        odds_paths = sorted(listdir_fullpath(ROOT_PATH + f"/Data/Odds/{self.league}/"))
        for odds_path in tqdm(odds_paths):
            odds_df = pd.read_excel(odds_path)
            season = self.odds_path_to_season(odds_path)
            row_pairs = self.odds_df_to_row_pairs(odds_df)

            seen_january = False
            for row_pair in tqdm(row_pairs):
                seen_january = True if seen_january else self.check_game_in_january(row_pair)
                df = self.row_pair_to_df(row_pair, df, season, seen_january)

        df.to_csv(ROOT_PATH + f"/Data/Odds/{self.league}.csv", index=False)


if __name__ == '__main__':
    leagues = ['NFL', 'NBA', 'NCAAF', 'NCAAB']
    for league in leagues:
        x = SBO_Clean_Data(league)
        x.run()
