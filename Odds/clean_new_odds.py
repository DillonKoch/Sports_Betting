# ==============================================================================
# File: clean_new_odds.py
# Project: Odds
# File Created: Saturday, 24th October 2020 8:28:10 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 24th October 2020 10:19:53 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Loads raw .xlsx files from the odds website and creates a clean .csv
# adds 2 columns to original file: Season and datetime
# ==============================================================================

import datetime
import os
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class Clean_New_Odds:
    def __init__(self):
        pass

    def load_xlsx_paths(self, league):  # Top Level  Tested
        """
        loads the .xlsx paths for a league
        """
        files = listdir_fullpath(ROOT_PATH + f"/Odds/{league}/")
        xlsx_files = [file for file in files if file[-5:] == '.xlsx']
        return xlsx_files

    def load_df(self, df_path):  # Top Level  Tested
        """
        loads a .xlsx path into a pd.DataFrame
        """
        df = pd.read_excel(df_path)
        return df

    def add_season_col(self, df, df_path):  # Top Level  Tested
        """
        adds a 'Season' column to the raw odds dataframe
        - season is the year the season began, so the 2018-19 season is just 2018
        """
        season = df_path.split('.')[0][-7:-3]
        df['Season'] = season
        return df

    def _datetime_years(self, date_strs, df_path):  # Specific Helper add_datetime_col  Tested
        """
        uses the 3-4 digit date strings from the odds df to create a list of
        years each row belongs to
        - in every league once the first January game appears, the year increases 1
        """
        start_year = int(df_path.split('.')[0][-7:-3])
        end_year = start_year + 1

        in_start_year = True
        years = []
        for date_str in date_strs:
            if ((len(date_str) == 3) and (date_str[0] == '1')):
                in_start_year = False

            if in_start_year:
                years.append(start_year)
            else:
                years.append(end_year)
        return years

    def add_datetime_col(self, df, df_path):  # Top Level  Tested
        """
        adds a datetime column to the odds df using the season from df_path
        and the 3-4 digit date strings representing date/month
        """
        date_strs = [str(item) for item in list(df['Date'])]
        years = self._datetime_years(date_strs, df_path)
        months = [ds[:2] if len(ds) == 4 else ds[0] for ds in date_strs]
        days = [ds[2:] if len(ds) == 4 else ds[1:] for ds in date_strs]

        df_datetimes = []
        for day, month, year in zip(days, months, years):
            current_dt = datetime.datetime(int(year), int(month), int(day))
            df_datetimes.append(current_dt)

        df['datetime'] = pd.Series(df_datetimes)
        return df

    def save_df(self, df, df_path):  # Top Level
        """
        saving the df to the same filename, but with .csv
        """
        csv_path = df_path.replace('.xlsx', '.csv')
        df.to_csv(csv_path, index=False)

    def run(self, league):  # Run
        df_paths = self.load_xlsx_paths(league)
        for df_path in df_paths:
            df = self.load_df(df_path)
            df = self.add_season_col(df, df_path)
            df = self.add_datetime_col(df, df_path)
            self.save_df(df, df_path)


if __name__ == '__main__':
    x = Clean_New_Odds()
    self = x
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        x.run(league)
