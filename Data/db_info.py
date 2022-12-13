# ==============================================================================
# File: db_info.py
# Project: allison
# File Created: Saturday, 10th December 2022 6:47:26 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 10th December 2022 6:47:26 pm
# Modified By: Dillon Koch
# -----
#
# -----
# providing information about the database
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Data.db_login import db_cursor


class DB_Info:
    def __init__(self):
        self.db, self.cursor = db_cursor()

    def get_cols(self, table):  # Run
        """
        returning a list of column names of a table in ordinal position
        """
        self.cursor.execute("USE sports_betting;")
        sql = f"SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_NAME = '{table}' ORDER BY ORDINAL_POSITION;"
        self.cursor.execute(sql)
        cols = [item[0] for item in self.cursor.fetchall()]
        return cols


if __name__ == '__main__':
    x = DB_Info()
    self = x
    x.get_cols("ESPN_Games_NFL")
