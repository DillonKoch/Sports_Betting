# ==============================================================================
# File: espn_to_database.py
# Project: ESPN
# File Created: Saturday, 29th August 2020 4:40:29 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 29th August 2020 4:51:05 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Adding ESPN Data to the database
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.sqlite_util import Sqlite_util
from Utility.Utility import listdir_fullpath, parse_league


class ESPN_To_Database:
    def __init__(self):
        pass

    def add_one_league(self, league):  # Run
        """
        adding all the team csv's in the league to the database
        """
        s = Sqlite_util()
        files = listdir_fullpath(ROOT_PATH + "/ESPN/Data/{}/".format(league))
        for file in files:
            df = pd.read_csv(file)
            df_db_name = file.split('/')[-1]
            df_db_name = "ESPN_NBA_" + df_db_name.split('.')[0]
            s.insert_df(df, df_db_name)
        print("all {} files uploaded to the database!".format(league).upper())

    def add_all_leagues(self):  # Run
        for league in ["NFL", "NBA", "NCAAF", "NCAAB"]:
            self.add_one_league(league)


if __name__ == "__main__":
    x = ESPN_To_Database()
    self = x
    league = parse_league()
    x.add_one_league(league)
