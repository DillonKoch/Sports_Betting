# ==============================================================================
# File: sbro.py
# Project: allison
# File Created: Tuesday, 22nd November 2022 1:28:58 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 22nd November 2022 1:28:59 pm
# Modified By: Dillon Koch
# -----
#
# -----
#
# ==============================================================================


import warnings
import os
import re
import string
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Data_Cleaning.match_team import Match_Team
from Data_Cleaning.dataset_validator import Dataset_Validator


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class SBRO:
    def __init__(self, league):
        warnings.filterwarnings('ignore')
        self.league = league
        self.match_team = Match_Team(league)
        self.dataset_validator = Dataset_Validator()
        self.valid_teams = self.match_team.list_valid_teams()

        self.df_cols = ['Season', 'Date', 'Home', 'Away', 'Is_Neutral',
                        'OU_Open', 'OU_Open_ML', 'OU_Close', 'OU_Close_ML', 'OU_2H', 'OU_2H_ML',
                        'Home_Line_Open', 'Home_Line_Open_ML', 'Away_Line_Open', 'Away_Line_Open_ML',
                        'Home_Line_Close', 'Home_Line_Close_ML', 'Away_Line_Close', 'Away_Line_Close_ML',
                        'Home_Line_2H', 'Home_Line_2H_ML', 'Away_Line_2H', 'Away_Line_2H_ML',
                        'Home_ML', 'Away_ML']

    def load_xlsx_paths(self):  # Top Level
        """
        loading full paths to .xlsx files for a given league
        """
        folder = ROOT_PATH + f"/Data/Odds/{self.league}/"
        paths = sorted(listdir_fullpath(folder))
        paths = [path for path in paths if "~lock" not in path]
        return paths

    def _clean_dates(self, df):  # Specific Helper clean_odds_df
        """
        manually cleaning dates that are not accurate in raw data and returning df
        """
        for i, date in enumerate(list(df['Date'])):
            # * manual correction - date was "7" for 2011-12 NCAAB Kentucky game row 7501
            if date == 7 and df['Rot'][i] == 874 and df['Team'][i] == 'Kentucky':
                df['Date'][i] = 323
                date = 323

            # * manual correctino - date was "1192" for 2012-13 NCAAF WashingtonU game row 1112
            if date == 1192 and df['Rot'][i] == 309 and df['Team'][i] == 'WashingtonU':
                df['Date'][i] = 1102
                date = 1102

        return df

    def _clean_quarter_half_final(self, df):  # Specific Helper clean_odds_df
        """
        cleaning quarter/half/final values to int's and 0-200 or nan
        """
        for col in ['1st', '2nd', '3rd', '4th', 'Final']:
            if col in list(df.columns):
                df[col] = self.dataset_validator.set_to_nan(df[col], valid_types=(int, float, np.number), min_val=0, max_val=200)
        return df

    def _clean_bet_vals(self, df):  # Specific Helper clean_odds_df
        """
        cleaning bet values by running replacements, splitting on values, and converting to floats
        """
        replace_val_combos = [(',', '.'), ('½', '.5'), ('..', '.'), ('ev', '')]
        split_val_combos = [('u', True), ('o', True), ('+', True)]
        replace_equals = [('p', 'pk', True), ("PK", "pk", False)]
        for col in ['Open', 'Close', 'ML', '2H']:
            df[col] = self.dataset_validator.float_if_possible(df[col])

            for (replace_val, new_val) in replace_val_combos:
                df[col] = self.dataset_validator.replace_vals(df[col], replace_val, new_val)

            df[col] = self.dataset_validator.split_vals(df[col], '-', True, start=1)  # 6-209
            for (split_str, keep_before) in split_val_combos:
                df[col] = self.dataset_validator.split_vals(df[col], split_str, keep_before)

            for (replace_val, new_val, set_lower) in replace_equals:
                df[col] = self.dataset_validator.replace_vals_equal(df[col], replace_val, new_val, set_lower=set_lower)

            vals = df[col]
            for i, val in enumerate(vals):
                if len(str(val)) > 0 and str(val)[0] == '+':  # fixing "+145\xao"
                    val = float(''.join(char for char in val if char in string.digits))

            df[col] = self.dataset_validator.float_if_possible(df[col])

        return df

    def _clean_moneyline(self, df):  # Specific Helper clean_odds_df
        """
        setting NULL/invlaid values to np.nan
        """
        for i, ml in enumerate(list(df['ML'])):
            if ml == "NL":
                df['ML'][i] = np.nan

            elif not isinstance(ml, (int, float)):
                df['ML'][i] = np.nan

            elif not ((float(ml) <= -100) or (float(ml) >= 100)) and 'nan' not in str(ml):
                df['ML'][i] = np.nan
                print(f"ML {ml} -> np.nan")

        return df

    def _clean_no_lines(self, df):  # Specific Helper clean_odds_df
        """
        NL's to np.nan
        """
        df["ML"] = self.dataset_validator.set_to_nan(df["ML"], invalid_vals=['NL'])
        df["Open"] = self.dataset_validator.set_to_nan(df["Open"], invalid_vals=['NL'])
        df["Close"] = self.dataset_validator.set_to_nan(df["Close"], invalid_vals=['NL'])
        df["2H"] = self.dataset_validator.set_to_nan(df["2H"], invalid_vals=['NL'])
        return df

    def clean_odds_df(self, df):  # Top Level
        """
        cleaning the raw odds df from SBRO as best as possible
        """
        df = self._clean_dates(df)
        df = self._clean_quarter_half_final(df)
        df = self._clean_bet_vals(df)
        df = self._clean_moneyline(df)
        df = self._clean_no_lines(df)

        # * moneyline "pk" to 100, others are edited later looking at both rows together
        df["ML"] = df["ML"].replace("pk", 100)

        return df

    def _dates_qa(self, df):  # Specific Helper odds_df_quality_assurance
        """
        checking dates are ints, 3-4 characters, chars are valid months/days
        """
        for date in list(df['Date']):
            assert isinstance(date, int), f"{date} is not an int"
            assert len(str(date)) in [3, 4], f"length of date {date} is not valid"
            if len(str(date)) == 4:
                assert str(date)[:2] in ['10', '11', '12'], f"{date} is not valid date"
            else:
                assert str(date)[0] in '123456789', f"{date} is not valid date"

            assert 1 <= int(str(date)[-2:]) <= 31, f"{date} day of month is not valid"

    def _vhn_qa(self, df):  # Specific Helper odds_df_quality_assurance
        """
        'VH' column must have "V", "H", "N" (neutral) or be np.nan
        """
        for vhn in list(df['VH']):
            assert (isinstance(vhn, str) and vhn in 'VHN') or np.isnan(vhn), f"{vhn} is not a string for VHN"

    def _team_names_qa(self, df):  # Specific Helper odds_df_quality_quality_assurance
        """
        asserting that every team name is one of the valid ones in /Data/Teams or is np.nan
        """
        for team in list(df['Team']):
            assert team in self.valid_teams or np.isnan(team), f"{team} not in valid teams!"

    def _quarter_half_final_qa(self, df):  # Specific Helper odds_df_quality_assurance
        """
        asserting quarter/half/final values are int/float, and in the range 0-200
        """
        for col in ['1st', '2nd', '3rd', '4th', 'Final']:
            if col in df.columns:
                vals = list(df[col])
                for val in vals:
                    assert isinstance(val, (int, float)), f"{val} is not an integer for col {col}"
                    assert np.isnan(val) or 0 <= val <= 200

    def _odds_qa(self, df):  # Specific Helper odds_df_quality_assurance
        """
        asserting values are int/float/"pk" and that moneylines are int/float/np.nan and abs(ml) >= 100
        """
        for col in ['Open', 'Close', '2H']:
            vals = df[col]
            for val in vals:
                assert isinstance(val, (int, float)) or val == "pk", f"{val} is not a number for col {col}"

        for ml in df['ML']:
            assert isinstance(ml, (int, float)), f"{ml} is not a number for ML"
            assert abs(ml) >= 100 or np.isnan(ml), f"{ml} is not a valid moneyline"

    def odds_df_quality_assurance(self, df):  # QA Testing
        """
        I'm supposed to check every df, and of course the one year I blow it off this happens!
        """
        self._dates_qa(df)
        self._vhn_qa(df)
        self._team_names_qa(df)
        self._quarter_half_final_qa(df)
        self._odds_qa(df)

    def _odds_path_to_season(self, odds_path):  # Specific Helper  odds_df_to_one_row
        """
        finds the season string inside the odds df path (like 2020-21)
        """
        filename = odds_path.split('/')[-1]
        season = re.findall(re.compile(r"\d{4}-\d{2}"), filename)[0]
        return season

    def _odds_df_to_row_pairs(self, odds_df):  # Specific Helper  odds_df_to_one_row
        """
        converts the odds dataframe into a list of row pairs, since each game has 2 rows in the df
        """
        row_lists = odds_df.values.tolist()
        row_pairs = [(row_lists[i], row_lists[i + 1]) for i in range(0, len(row_lists), 2)]
        return row_pairs

    def odds_df_to_one_row(self, path, df):  # Top Level
        """
        converting the odds_df from two cols per game to just one
        """
        clean_df = pd.DataFrame(columns=self.df_cols)
        season = self._odds_path_to_season(path)
        row_pairs = self._odds_df_to_row_pairs(df)

        seen_january = False
        for row_pair in tqdm(row_pairs):
            seen_january = True if seen_january else self._check_game_in_january(row_pair)
            clean_df = self._row_pair_to_df(row_pair, clean_df, season, seen_january)

    def df_to_db(self, df):  # Top Level
        pass

    def run(self):  # Run
        xlsx_paths = self.load_xlsx_paths()
        odds_dfs = [pd.read_excel(xlsx_path) for xlsx_path in tqdm(xlsx_paths)]
        for i, odds_df in enumerate(odds_dfs):
            odds_df = self.clean_odds_df(odds_df)
            self.odds_df_quality_assurance(odds_df)
            # df = self.odds_df_to_one_row(xlsx_path, odds_df)
            # self.df_to_db(df)
            odds_dfs[i] = odds_df

        full_df = pd.concat(odds_dfs)
        self.dataset_validator.dataset_info(full_df)


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        x = SBRO(league)
        self = x
        x.run()
