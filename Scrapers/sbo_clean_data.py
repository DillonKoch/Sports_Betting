# ==============================================================================
# File: sbo_clean_data.py
# Project: Scrapers
# File Created: Saturday, 12th June 2021 10:08:31 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 12th June 2021 10:08:34 pm
# Modified By: Dillon Koch
# -----
#
# -----
# merges the individual .xlsx files in /Data/Odds/<league> to /Data/Odds/<league>/<league>_SBO.csv
# ==============================================================================

import concurrent.futures
import datetime
import os
import re
import string
import sys
from operator import itemgetter
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.match_team import Match_Team


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def multithread(func, func_args):  # Multithreading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = list(tqdm(executor.map(func, func_args), total=len(func_args)))
    return result


class Sbo_Clean_Data:
    def __init__(self):
        self.df_cols = ["Season", "Date", "Home", "Away", "is_neutral",
                        "H1Q", "H2Q", "H3Q", "H4Q", "H1H", "H2H", "HOT", "HFinal",
                        "A1Q", "A2Q", "A3Q", "A4Q", "A1H", "A2H", "AOT", "AFinal",
                        "OU_Open", "OU_Open_ML", "OU_Close", "OU_Close_ML", "OU_2H", "OU_2H_ML",
                        "Home_Spread_Open", "Home_Spread_Open_ML",
                        "Home_Spread_Close", "Home_Spread_Close_ML",
                        "Home_Spread_2H", "Home_Spread_2H_ML",
                        "Away_Spread_Open", "Away_Spread_Open_ML",
                        "Away_Spread_Close", "Away_Spread_Close_ML",
                        "Away_Spread_2H", "Away_Spread_2H_ML",
                        "Home_ML", "Away_ML"]
        self.match_team = Match_Team()

    def _df_to_row_pairs(self, df):  # Global Helper  Tested
        """
        converts a pd.DataFrame to a list of lists with the df's values
        (just easier to work with than a df sometimes)
        """
        row_lists = df.values.tolist()
        row_pairs = [(row_lists[i], row_lists[i + 1]) for i in range(0, len(row_lists), 2)]
        return row_pairs

    def add_season(self, odds_df, odds_df_path):  # Top Level  Tested
        """
        adds the season in format 2020-21 to the dataframe
        """
        filename = odds_df_path.split('/')[-1]
        season = re.findall(re.compile(r"\d{4}-\d{2}"), filename)[0]
        odds_df['Season'] = season
        return odds_df

    def add_overtime(self, odds_df, league):  # Top Level  Tested
        """
        adds an overtime column to the dataframe based on scores in the 4q's or 2h's and final
        """
        col_1st = odds_df['1st']
        col_2nd = odds_df['2nd']
        col_3rd = odds_df['3rd'] if league != "NCAAB" else None
        col_4th = odds_df['4th'] if league != "NCAAB" else None
        col_final = odds_df['Final']
        odds_df['OT'] = col_final - col_1st - col_2nd
        odds_df['OT'] = odds_df['OT'] - col_3rd - col_4th if league != "NCAAB" else odds_df['OT']
        return odds_df

    def add_ml_cols(self, odds_df):  # Top Level  Tested
        """
        Adds ML columns for the open/close/2h lines
        (sometimes they're not -110 so this col includes those rare differences)
        """
        # TODO change "open_vals" variable name
        # TODO need to change the original column too so it doesn't have "12-109" type stuff
        for ml_col in ["Open", "Close", "2H"]:
            open_vals = list(odds_df[ml_col])
            new_open_vals = []
            new_open_mls = []
            for open_val in open_vals:
                match = re.match(re.compile(r"((((\d{1,3}\.?)+)|pk))-(\d{3})"), str(open_val))
                new_open_val = match.group(1) if match else open_val
                new_open_ml = '-' + match.group(5) if match else -110
                new_open_vals.append(new_open_val)
                new_open_mls.append(new_open_ml)
            odds_df[ml_col] = pd.Series(new_open_vals)
            odds_df[ml_col + "_ML"] = pd.Series(new_open_mls)
        return odds_df

    def reorder_cols(self, odds_df, league):  # Top Level  Done
        """
        simply reorders the columns in odds_df to make more sense
        """
        col_order = ["Season", "Date", "Rot", "VH", "Team", "1st", "2nd", "3rd", "4th", "OT",
                     "Final", "Open", "Open_ML", "Close", "Close_ML", "ML", "2H", "2H_ML"]
        col_order = [col for col in col_order if col not in ['3rd', '4th']] if league == "NCAAB" else col_order
        odds_df = odds_df[col_order]
        return odds_df

    def _test_na_values(self, odds_df):  # Specific Helper test_odds_df
        """
        tests that the columns don't have any NA values
        """
        cols = list(odds_df.columns)
        cols.remove("Rot")
        for col in cols:
            err_msg = f"col {col} has an empty value"
            assert odds_df[col].isnull().sum() == 0, err_msg

    def _test_date(self, row1, row2):  # Specific Helper test_odds_df
        """
        testing that the dates for the two rows in a game are valid and match
        """
        row1_date = row1[1]
        row1_team = row1[4]
        row2_date = row2[1]
        row2_team = row2[4]
        for date in [row1_date, row2_date]:
            assert isinstance(date, int), f"invalid date - {date}"
            assert len(str(date)) in [3, 4], f"invalid date - {date}"

        assert row1_date == row2_date, f"Dates {row1_date}, {row2_date} don't match for {row1_team}, {row2_team}"

    def _test_vh(self, row1, row2):  # Specific Helper test_odds_df
        """
        testing that the visitor/home values match up appropriately
        """
        row1_vh = row1[3]
        row2_vh = row2[3]
        err_msg = f"Home-Away not valid for {row1[1]} {row1[4]} vs {row2[4]}: {row1_vh}, {row2_vh}"
        assert [row1_vh, row2_vh] in [["H", "V"], ["V", "H"], ["N", "N"]], err_msg

    def _test_team(self, row):  # Specific Helper test_odds_df
        team = row[4].strip()
        err_msg = f"invalid team - '{team}'"
        assert isinstance(team, str), err_msg
        valid_chars = string.ascii_letters + ".&-()', "
        for char in team:
            assert char in valid_chars, err_msg

    def _test_score(self, row, league):  # Specific Helper test_odds_df
        """
        testing that the 4 quarters / 2 halves (and overtime) add to the final score
        """
        p1 = row[5]
        p2 = row[6]
        p3 = row[7] if league != "NCAAB" else 0
        p4 = row[8] if league != "NCAAB" else 0
        ot = row[9] if league != "NCAAB" else row[7]
        final = row[10] if league != "NCAAB" else row[8]
        # testing that the scores are ints
        for score_val in [p1, p2, p3, p4, ot, final]:
            assert isinstance(score_val, int)

        # testing that the scores add up to the final
        err_msg = f"Scores don't add up for {row[0]} {row[1]} {row[4]}"
        assert sum([int(p1), int(p2), int(p3), int(p4), int(ot)]) == int(final), err_msg

    def _test_odds(self, row):  # Specific Helper test_odds_df
        open_odds = row[-4]
        close_odds = row[-3]
        ml_odds = row[-2]
        second_half_odds = row[-1]
        for odd_val in [open_odds, close_odds, ml_odds, second_half_odds]:
            if odd_val not in ['pk', 'NL']:
                assert isinstance(float(odd_val), float), f"error - {odd_val} is type {type(odd_val)}"

    def test_odds_df(self, odds_df, league):  # Top Level
        """
        runs data quality tests to make sure the data is valid
        Tested - this method and its helper methods are all tests, so I won't test them
        """
        self._test_na_values(odds_df)
        row_pairs = self._df_to_row_pairs(odds_df)
        for i, row_pair in enumerate(row_pairs):
            row1, row2 = row_pair
            self._test_date(row1, row2)
            self._test_vh(row1, row2)
            self._test_team(row1)
            self._test_team(row2)
            self._test_score(row1, league)
            self._test_score(row2, league)
            self._test_odds(row1)
            self._test_odds(row2)

    def _home_away_row(self, row_pair):  # Specific Helper odds_to_clean_df
        """
        returns (home_row, away_row) depending on the VH column
        """
        row1, row2 = row_pair
        return (row1, row2) if row1[3] in ["H", "N"] else (row2, row1)

    def _season_date(self, row, past_new_years):  # Specific Helper odds_to_clean_df
        """
        returns the season in "2020-21" format and a datetime str for the game date
        """
        season = row[0]
        date = str(row[1])
        if not past_new_years:
            if ((len(date) == 3) and (date[0] == '1')):
                past_new_years = True

        year = int(season[:4]) + 1 if past_new_years else int(season[:4])
        month = date[:2] if len(date) == 4 else date[0]
        day = date[-2:]
        datetime_str = datetime.date(int(year), int(month), int(day)).strftime("%Y-%m-%d")
        return season, datetime_str, past_new_years

    def _home_away_info(self, home_row, away_row, league):  # Specific Helper odds_to_clean_df
        """
        returns the (home, away, is_neutral) data from the two game rows
        - uses the Match_Team class to find the closest team name match
        """
        home = self.match_team.run(league, home_row[4])
        away = self.match_team.run(league, away_row[4])
        is_neutral = 1 if home_row[3] == "N" else 0
        return home[0], away[0], is_neutral

    def _score_vals(self, row):  # Specific Helper odds_to_clean_df
        """
        returns all the score values for one team given its row in the game
        """
        if league == "NCAAB":
            t1h, t2h, tot, tfinal = row[5:9]
            t1q = None
            t2q = None
            t3q = None
            t4q = None
        else:
            t1q, t2q, t3q, t4q, tot, tfinal = row[5:11]
            t1h = None
            t2h = None

        return t1q, t2q, t3q, t4q, t1h, t2h, tot, tfinal

    def _rows_to_val_pairs(self, home_row, away_row, val_index, ml_index):  # Helping Helper
        """
        using the home/away rows, this method uses the indices given to produce pairs of (val, ml)
        """
        home_row_val = home_row[val_index] if home_row[val_index] != 'pk' else 0
        home_row_ml = home_row[ml_index]
        away_row_val = away_row[val_index] if away_row[val_index] != 'pk' else 0
        away_row_ml = away_row[ml_index]
        pairs = [(home_row_val, home_row_ml), (away_row_val, away_row_ml)]
        return pairs

    def _ou_line_pairs(self, pairs):  # Helping Helper
        ou_pair = max(pairs, key=itemgetter(0))
        line_pair = min(pairs, key=itemgetter(0))
        return ou_pair, line_pair

    def _line_pairs_to_home_away(self, pairs, line_pair):  # Helping Helper
        line_pair_is_home = line_pair == pairs[0]
        home_line = line_pair[0] if line_pair_is_home else (-1 * line_pair[0])
        home_line_ml = line_pair[1] if line_pair_is_home else (-220 - line_pair[1])
        away_line = home_line * -1
        away_line_ml = -220 - home_line_ml
        return home_line, home_line_ml, away_line, away_line_ml

    def _bet_vals(self, home_row, away_row, val_index, ml_index):  # Specific Helper
        pairs = self._rows_to_val_pairs(home_row, away_row, val_index, ml_index)
        ou_pair, line_pair = self._ou_line_pairs(pairs)
        hline, hline_ml, aline, aline_ml = self._line_pairs_to_home_away(pairs, line_pair)
        return ou_pair[0], ou_pair[1], hline, hline_ml, aline, aline_ml

    def odds_to_clean_df(self, odds_df, league):  # Top Level
        """
        converts the odds_df to a clean_df, with one row per game
        """
        row_pairs = self._df_to_row_pairs(odds_df)
        clean_rows = []
        past_new_years = False
        for row_pair in row_pairs:
            home_row, away_row = self._home_away_row(row_pair)
            season, date, past_new_years = self._season_date(home_row, past_new_years)
            home, away, is_neutral = self._home_away_info(home_row, away_row, league)
            h1q, h2q, h3q, h4q, h1h, h2h, hot, hfinal = self._score_vals(home_row)
            a1q, a2q, a3q, a4q, a1h, a2h, aot, afinal = self._score_vals(away_row)
            ou_open, ou_open_ml, hline_open, hline_open_ml, aline_open, aline_open_ml = self._bet_vals(home_row, away_row, -7, -6)
            ou_close, ou_close_ml, hline_close, hline_close_ml, aline_close, aline_close_ml = self._bet_vals(
                home_row, away_row, -5, -4)
            ou_2h, ou_2h_ml, hline_2h, hline_2h_ml, aline_2h, aline_2h_ml = self._bet_vals(home_row, away_row, -2, -1)
            home_ml = home_row[-3]
            away_ml = away_row[-3]

            new_clean_row = [season, date, home, away, is_neutral,
                             h1q, h2q, h3q, h4q, h1h, h2h, hot, hfinal,
                             a1q, a2q, a3q, a4q, a1h, a2h, aot, afinal,
                             ou_open, ou_open_ml, ou_close, ou_close_ml, ou_2h, ou_2h_ml,
                             hline_open, hline_open_ml, hline_close, hline_close_ml, hline_2h, hline_2h_ml,
                             aline_open, aline_open_ml, aline_close, aline_close_ml, aline_2h, aline_2h_ml,
                             home_ml, away_ml]
            clean_rows.append(new_clean_row)

        clean_df = pd.DataFrame(clean_rows, columns=self.df_cols)
        return clean_df

    def save_full_df(self, df, league):  # Top Level
        path = ROOT_PATH + f"/Data/Odds/{league}.csv"
        df.to_csv(path, index=False)
        print('saved!')

    def run(self, league):  # Run
        odds_df_paths = sorted(listdir_fullpath(ROOT_PATH + f"/Data/Odds/{league}/"))
        clean_dfs = []
        for odds_df_path in odds_df_paths:
            print(odds_df_path.split('/')[-1])
            odds_df = pd.read_excel(odds_df_path)
            odds_df = self.add_season(odds_df, odds_df_path)
            odds_df = self.add_overtime(odds_df, league)
            odds_df = self.add_ml_cols(odds_df)
            odds_df = self.reorder_cols(odds_df, league)
            self.test_odds_df(odds_df, league)
            clean_df = self.odds_to_clean_df(odds_df, league)
            clean_dfs.append(clean_df)
        full_clean_df = pd.concat(clean_dfs)
        self.save_full_df(full_clean_df, league)
        return full_clean_df

    def run_all(self):  # Run
        for league in ["NFL", "NCAAF", "NBA", "NCAAB"]:
            self.run(league)

    def full_raw_df(self, league):  # Run
        odds_df_paths = sorted(listdir_fullpath(ROOT_PATH + f"/Data/Odds/{league}/"))
        dfs = [pd.read_excel(odds_df_path) for odds_df_path in tqdm(odds_df_paths)]
        full_raw_df = pd.concat(dfs)
        return full_raw_df

    def show_team_matches(self, league):  # QA Testing
        """
        prints out the team matches from the teams given in the Odds data
        """
        frd = self.full_raw_df(league)
        teams = list(set(list(frd['Team'])))

        combos = []
        for team in teams:
            match, match_ratio = x.match_team.run(league, team)
            combos.append((match, match_ratio, team))

        combos = sorted(combos, key=itemgetter(1), reverse=True)
        for combo in combos:
            print(combo[2])
            print(combo[0], combo[1])
            print('\n')


if __name__ == '__main__':
    x = Sbo_Clean_Data()
    self = x
    league = "NBA"
    full_df = x.run(league)
    # x.run_all()
    # x.show_team_matches(league)
