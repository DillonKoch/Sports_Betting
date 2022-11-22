# ==============================================================================
# File: sbro.py
# Project: allison
# File Created: Friday, 18th November 2022 11:06:15 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 18th November 2022 11:06:16 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Cleaning .xlsx SBRO files and inserting data into MySQL database
# only updating database if new entries are found (via newly downloaded .xlsx files)
# ==============================================================================

import datetime
import os
import re
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Data.db_login import db_cursor

from Data_Cleaning.match_team import Match_Team


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class Clean_SBRO:
    def __init__(self, league):
        self.league = league
        self.match_team = Match_Team()
        self.db, self.cursor = db_cursor()

        self.df_cols = ['Season', 'Date', 'Home', 'Away', 'Is_Neutral',
                        'OU_Open', 'OU_Open_ML', 'OU_Close', 'OU_Close_ML', 'OU_2H', 'OU_2H_ML',
                        'Home_Line_Open', 'Home_Line_Open_ML', 'Away_Line_Open', 'Away_Line_Open_ML',
                        'Home_Line_Close', 'Home_Line_Close_ML', 'Away_Line_Close', 'Away_Line_Close_ML',
                        'Home_Line_2H', 'Home_Line_2H_ML', 'Away_Line_2H', 'Away_Line_2H_ML',
                        'Home_ML', 'Away_ML']

    def load_xlsx_paths(self, league):  # Top Level
        """
        loading full paths to .xlsx files for a given league
        """
        folder = ROOT_PATH + f"/Data/Odds/{league}/"
        paths = sorted(listdir_fullpath(folder))
        return paths

    def _clean_bet_val(self, bet_val):
        bet_val = bet_val.replace('½', '.5') if isinstance(bet_val, str) else bet_val
        if ',' in str(bet_val):
            bet_val = float(bet_val.replace(",", "."))
        if '..' in str(bet_val):
            bet_val = float(bet_val.replace('..', '.'))
        if 'ev' in str(bet_val):
            bet_val = float(bet_val.replace('ev', ''))
        if 'u' in str(bet_val):
            print(f"FOUND A U: {bet_val}")
            bet_val = float(str(bet_val).split('u')[0])
        if 'o' in str(bet_val):
            print(f"FOUND A O: {bet_val}")
            bet_val = float(str(bet_val).split('o')[0])
        if '+' in str(bet_val):
            print(f"FOUND A +: {bet_val}")
            bet_val = float(str(bet_val).split('+')[0])

    def clean_values(self, df, season):  # Specific Helper clean_df
        """
        cleaning values in the dataframe
        """
        # TODO manual date corrections, bet value corrections, alter team names
        print('here')

    def odds_path_to_season(self, odds_path):  # Specific Helper
        """
        finds the season string inside the odds df path (like 2020-21)
        """
        filename = odds_path.split('/')[-1]
        season = re.findall(re.compile(r"\d{4}-\d{2}"), filename)[0]
        return season

    def odds_df_to_row_pairs(self, odds_df):  # Specific Helper
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
        # ! IF DATES NOT EQUAL, TAKE FIRST ROW'S
        # TODO I'll have to make some manual corrections, date must be correct for merging
        if date1 != date2:
            print(f"INVALID DATES FOUND: {date1}, {date2}. Keeping {date1}")
            if date1 == '1192':
                date1 = '1102'
                date2 = '1102'
            date2 = date1
            assert isinstance(date1, str)
            _ = int(date1)
        # assert date1 == date2

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

        # ! IF THE HOME-AWAY VALUES ARE NOT VALID, SET TO NEUTRAL GAME
        if [row1_vh, row2_vh] not in [['V', 'H'], ['H', 'V'], ['N', 'N']]:
            print(f"Home-Away values not valid: {row1_vh}, {row2_vh}")
            row1_vh = 'N'
            row2_vh = 'N'
        # assert [row1_vh, row2_vh] in [['V', 'H'], ['H', 'V'], ['N', 'N']], f"{row1_vh}, {row2_vh}"

        row1_home = row1_vh in ['H', 'N']
        home_row = row1 if row1_home else row2
        away_row = row2 if row1_home else row1
        return home_row, away_row

    def _home_away_neutral(self, row_pair):  # Specific Helper row_pair_to_df
        """
        returns the home/away official name from the row pair, and whether the game is at a neutral location
        """
        home_row, away_row = self._home_away_row(row_pair)
        home = self.match_team.run(self.league, home_row[3])
        away = self.match_team.run(self.league, away_row[3])
        is_neutral = 1 if home_row[2] == 'N' else 0
        return home, away, is_neutral

    def _bet_val_to_val_ml(self, bet_val):  # Helping Helper _open_close_2h_bets
        """
        converts the bet_val from the odds df into either the val, None or the val, ML
        - ML only shows up when the bet_val is in format 7-105
        """
        bet_val = bet_val.replace('½', '.5') if isinstance(bet_val, str) else bet_val
        if ',' in str(bet_val):
            bet_val = float(bet_val.replace(",", "."))
        if '..' in str(bet_val):
            bet_val = float(bet_val.replace('..', '.'))
        if 'ev' in str(bet_val):
            bet_val = float(bet_val.replace('ev', ''))
        if 'u' in str(bet_val):
            print(f"FOUND A U: {bet_val}")
            bet_val = float(str(bet_val).split('u')[0])
        if 'o' in str(bet_val):
            print(f"FOUND A O: {bet_val}")
            bet_val = float(str(bet_val).split('o')[0])
        if '+' in str(bet_val):
            print(f"FOUND A +: {bet_val}")
            bet_val = float(str(bet_val).split('+')[0])
        bet_val = abs(bet_val) if isinstance(bet_val, (int, float)) else bet_val
        try:
            bet_val = str(bet_val).lower().replace('pk', '0').replace("p", '0')
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
        if home_row[col_index] == '-' or away_row[col_index] == '-':
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
        if home_row[-2] == '-' or away_row[-2] == '-':
            return None, None
        home_ml = float(str(home_row[-2]).lower().replace('pk', '0').replace('½', '.5'))
        away_ml = float(str(away_row[-2]).lower().replace('pk', '0').replace('½', '.5'))
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
        new_row = [round(item, 1) if isinstance(item, float) else item for item in new_row]  # 1 decimal for SQL
        df.loc[len(df)] = new_row
        return df

    def clean_df(self, df, path):  # Top Level
        """
        converting the raw df from the excel file into a clean df
        to be uploaded into the database
        """
        clean_df = pd.DataFrame(columns=self.df_cols)
        season = self.odds_path_to_season(path)

        df = self.clean_values(df, season)
        row_pairs = self.odds_df_to_row_pairs(df)

        seen_january = False
        for row_pair in tqdm(row_pairs):
            seen_january = True if seen_january else self.check_game_in_january(row_pair)
            clean_df = self.row_pair_to_df(row_pair, clean_df, season, seen_january)

        return clean_df

    def insert_to_db(self, df):  # Top Level
        self.cursor.execute("USE sports_betting;")
        for i, row in df.iterrows():
            col_names = "(" + ', '.join(row.keys()) + ")"
            val_list = [f'"{i}"' if isinstance(i, str) or (i is not None and not np.isnan(i))
                        else "NULL" for i in row.values]
            vals = "(" + ', '.join(val_list) + ")"
            sql = f"INSERT IGNORE INTO SBRO_{self.league} {col_names} VALUES {vals};"
            self.cursor.execute(sql)
        self.db.commit()

    def run(self):  # Run
        """
        """
        print(self.league)
        # for every .xlsx file, load it, clean it, insert it to DB
        xlsx_paths = self.load_xlsx_paths(self.league)
        for path in xlsx_paths:
            print(path)
            df = pd.read_excel(path)
            df = self.clean_df(df, path)
            df.to_csv(f"({self.league})_temp.csv")
            self.insert_to_db(df)


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        # for league in ['NFL']:
        x = Clean_SBRO(league)
        self = x
        x.run()
