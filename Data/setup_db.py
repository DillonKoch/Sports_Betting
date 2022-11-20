# ==============================================================================
# File: setup_db.py
# Project: allison
# File Created: Friday, 18th November 2022 11:14:17 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 18th November 2022 11:14:17 pm
# Modified By: Dillon Koch
# -----
#
# -----
# performing operations to set up the database
# (assuming mysql set up and user 'Dillon'@'localhost' identified by 'password' created)
# - create databse if it doesn't exist
# -
# ==============================================================================

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Data.db_login import db_cursor


class Setup_DB:
    def __init__(self):
        self.mydb, self.cursor = db_cursor()
        self.leagues = ["NFL", "NBA", "NCAAF", "NCAAB"]

    def show_dbs(self):  # Top Level
        self.cursor.execute("SHOW DATABASES;")
        dbs = []
        for db in self.cursor:
            dbs.append(db[0])
        return dbs

    def show_tables(self):  # Top Level
        self.cursor.execute("SHOW TABLES;")
        tables = []
        for table in self.cursor:
            tables.append(table[0])
        return tables

    def create_sbro(self, tables, league):  # Top Level
        """
        """
        if f"SBRO_{league}" in tables:
            return None

        print("Creating SBRO Table...")
        vc = "VARCHAR(255)"
        dbl = "DOUBLE"
        i = "INT"
        sql = f"""CREATE TABLE SBRO_{league} (Season {vc}, Date DATE, Home {vc}, Away {vc},
                Is_Neutral BOOL, OU_Open {dbl}, OU_Open_ML {i}, OU_Close {dbl}, OU_Close_ML {i},
                OU_2H {dbl}, OU_2H_ML {i}, Home_Line_Open {dbl}, Home_Line_Open_ML {i},
                Away_Line_Open {dbl}, Away_Line_Open_ML {i}, Home_Line_Close {dbl},
                Home_Line_Close_ML {i}, Away_Line_Close {dbl}, Away_Line_Close_ML {i},
                Home_Line_2H {dbl}, Home_Line_2H_ML {i}, Away_Line_2H {dbl}, Away_Line_2H_ML {i},
                Home_ML {i}, Away_ML {i});"""
        self.cursor.execute(sql)

    def create_covers(self):  # Top Level
        pass

    def create_espn_games(self):  # Top Level
        pass

    def run(self):  # Run
        # * check if sports_betting database exists
        dbs = self.show_dbs()
        print(f"Current Databases: {dbs}")

        # * if not, create sports_betting database
        if 'sports_betting' not in dbs:
            self.cursor.execute("CREATE DATABASE sports_betting")

        self.cursor.execute("USE sports_betting;")

        # * create tables
        tables = self.show_tables()

        for league in self.leagues:
            self.create_sbro(tables, league)
            # TODO more tables


if __name__ == '__main__':
    x = Setup_DB()
    self = x
    x.run()
