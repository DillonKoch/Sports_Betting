# ==============================================================================
# File: clean_new_odds.py
# Project: Odds
# File Created: Monday, 24th August 2020 5:29:50 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 24th October 2020 1:39:26 pm
# Modified By: Dillon Koch
# -----
#
# -----
# File for cleaning incoming .xlsx odds files freshly downloaded
# ==============================================================================


import os
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.Utility import parse_league


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class Clean_New_Odds:
    """
    class to read in a freshly downloaded .xlsx file of odds
    and convert it into a usable .csv file in the same folder
    """

    def __init__(self, league):
        self.league = league

    def load_most_recent_xlsx(self):  # Top Level
        """
        loads the most recent .xlsx file in a league's odds folder
        - returns the df, season start year (to add a col) and filename
          of the .xlsx file to create an identical .csv file
        """
        league_files = listdir_fullpath(ROOT_PATH + "/Odds/{}".format(self.league))
        xlsx_files = [f for f in league_files if ".xlsx" in f]
        most_recent_xlsx = max(xlsx_files, key=lambda x: int(x.split('.')[0][-7:-3]))
        season_start_year = most_recent_xlsx.split('.')[0][-7:-3]
        df = pd.read_excel(most_recent_xlsx)
        return df, season_start_year, most_recent_xlsx

    def add_season_col(self, df, season_start_year):  # Top Level
        """
        adds a "Season" column to raw odds data
        """
        if "Season" in list(df.columns):
            return df
        else:
            df['Season'] = season_start_year
            return df

    def add_year_col(self, df):  # Top Level
        """
        adds the "Year" column to the raw odds data, that always shows the current year
        for each row, including after Jan 1 in the season
        - used for creating datetime column in odds_to_db.py
        """
        df['year'] = None
        start_year = int(df['Season'][0])

        past_new_years = False
        for i, row in df.iterrows():
            if not past_new_years:
                # if date is 3 characters and starts with 1 (January)
                if ((len(str(row['Date'])) == 3) and (str(row['Date'])[0] == '1')):
                    past_new_years = True

            if past_new_years:
                row['year'] = start_year + 1
                df.loc[i] = row
            else:
                row['year'] = start_year
                df.loc[i] = row
        return df

    def run(self):  # Run
        newest_xlsx, season_start_year, most_recent_xlsx = self.load_most_recent_xlsx()
        df = self.add_season_col(newest_xlsx, season_start_year)
        df = self.add_year_col(df)
        new_csv_path = most_recent_xlsx.replace('.xlsx', '.csv')
        df.to_csv(new_csv_path, index=False)
        print("Data saved to {}!".format(new_csv_path))


if __name__ == "__main__":
    league = "NFL"
    league = parse_league()
    x = Clean_New_Odds(league)
    self = x
    x.run()
