# ==============================================================================
# File: sqlite_util.py
# Project: Utility
# File Created: Saturday, 22nd August 2020 12:56:05 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 23rd August 2020 11:41:34 am
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
        print("connected to sports_betting.db")
        cursor = conn.cursor()
        return conn, cursor

    def insert_df(self, df, table_name):  # Run
        conn, cursor = self.connect_to_db()
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"inserted table {table_name} to the database!")


if __name__ == "__main__":
    x = Sqlite_util()
    self = x
    conn, cursor = x.connect_to_db()
