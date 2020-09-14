# ==============================================================================
# File: sqlite_util.py
# Project: Utility
# File Created: Saturday, 22nd August 2020 12:56:05 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 12th September 2020 7:43:41 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Utility functions for using the sqlite database in this repo
# ==============================================================================


import sqlite3
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Sqlite_util:
    def __init__(self):
        self.db_path = ROOT_PATH + "/sports_betting.db"

    def connect_to_db(self):  # Run
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        return conn, cursor

    def insert_df(self, df, table_name):  # Run
        conn, cursor = self.connect_to_db()
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"inserted table {table_name} to the database!")

    def add_main_data(self):
        leagues = ['NFL', 'NBA']
        for league in leagues:
            espn_df = pd.read_csv(ROOT_PATH + f"/ESPN/ML/{league}_ML.csv")
            self.insert_df(espn_df, f"{league}_ESPN")

            odds_df = pd.read_csv(ROOT_PATH + f"/Odds/{league}.csv")
            self.insert_df(odds_df, f"{league}_Odds")

            esb_df = pd.read_csv(ROOT_PATH + f"/ESB/Data/{league}/Game_Lines.csv")
            esb_df = esb_df.sort_values(by='scraped_ts')
            esb_df = esb_df.drop_duplicates(subset=['datetime', 'Home', 'Away'], keep='last')
            self.insert_df(esb_df, f"{league}_ESB")

            wh_df = pd.read_csv(ROOT_PATH + f"/WH/Data/{league}/Game_Lines.csv")
            wh_df = wh_df.sort_values(by='scraped_ts')
            wh_df = wh_df.drop_duplicates(subset=['datetime', 'Home', 'Away'], keep='last')
            self.insert_df(wh_df, f"{league}_WH")


if __name__ == "__main__":
    x = Sqlite_util()
    self = x
    self.add_main_data()
