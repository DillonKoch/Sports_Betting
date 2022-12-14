# ==============================================================================
# File: db_ops.py
# Project: allison
# File Created: Saturday, 10th December 2022 9:35:44 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 10th December 2022 9:35:45 pm
# Modified By: Dillon Koch
# -----
#
# -----
# class for common database operations to reduce duplicated code
# ==============================================================================


import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Data.db_info import DB_Info
from Data.db_login import db_cursor


class DB_Ops:
    def __init__(self):
        self.db, self.cursor = db_cursor()
        self.cursor.execute("USE sports_betting;")
        self.db_info = DB_Info()

    def update_row(self, table, row):  # Run
        """
        updates values of a row in table with the values passed in 'row'
        """
        cols = self.db_info.get_cols(table)
        row = [item if item is not None else "NULL" for item in row]
        cv_strs = []
        for col, val in zip(cols, row):
            cv_strs.append(f"{col} = '{val}'")
        updates = ', '.join(cv_strs)

        sql = f"UPDATE {table} SET {updates} WHERE Game_ID = {row[0]};"
        sql = sql.replace("'NULL'", "NULL")
        self.cursor.execute(sql)
        self.db.commit()

    def insert_row(self, table, row, ignore=False):  # Run
        ignore_str = "IGNORE " if ignore else ""
        cols = self.db_info.get_cols(table)
        col_names = "(" + ", ".join(cols) + ")"

        row = [item if item is not None else "NULL" for item in row]
        row = [item if str(item) != 'nan' else "NULL" for item in row]
        vals = "(" + ", ".join([f'"{i}"' for i in row]) + ")"
        sql = f"INSERT {ignore_str}INTO {table} {col_names} VALUES {vals};"
        sql = sql.replace('"NULL"', 'NULL')
        self.cursor.execute(sql)
        self.db.commit()

    def select_all(self, table):  # Run
        sql = f"SELECT * FROM {table};"
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        return data

    def save_table(self, table):  # Run
        """
        saving a table in the DB to a path
        """
        path = ROOT_PATH + f"/Data/{table}.csv"
        cols = self.db_info.get_cols(table)
        data = self.select_all(table)
        df = pd.DataFrame(data, columns=cols)
        print('here')
        df.to_csv(path, index=None)

    # def csv_to_table(self, table):  # Run
    #     """
    #     ! RAN THIS TO EDIT ESPN_GAMES_{LEAGUE} TABLES TO SPLIT DASH COLS
    #     """
    #     df = pd.read_csv(ROOT_PATH + f"/Data/{table}.csv")
    #     for i in tqdm(range(len(df))):
    #         row = list(df.iloc[i, :])
    #         new_row = []
    #         for i, item in enumerate(row):
    #             if i in [6, 7, 34, 35, 36, 37, 48, 49, 54, 55, 62, 63, 64, 65]:
    #                 if isinstance(item, str):
    #                     assert '-' in item, f"{item} has no -"

    #                     d1 = item.split(',')[0].split('-')[0]
    #                     d2 = item.split(',')[0].split('-')[1]

    #                     new_row.append(d1)
    #                     new_row.append(d2)
    #                 else:
    #                     new_row.append(None)
    #                     new_row.append(None)
    #             else:
    #                 new_row.append(item)
    #         self.insert_row(table, new_row, ignore=True)

    def csv_to_table(self, table):  # Run
        df = pd.read_csv(ROOT_PATH + f"/Data/{table}.csv")
        for i in tqdm(range(len(df))):
            row = list(df.iloc[i, :])
            self.insert_row(table, row, ignore=False)


if __name__ == '__main__':
    x = DB_Ops()
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        # x.save_table(f"ESPN_Games_{league}")
        # for league in ['NFL', 'NCAAF']:
        x.csv_to_table(f"ESPN_Games_{league}")
