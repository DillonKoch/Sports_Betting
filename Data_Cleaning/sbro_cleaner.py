# ==============================================================================
# File: sbro_cleaner.py
# Project: allison
# File Created: Friday, 26th August 2022 6:39:19 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 26th August 2022 6:39:19 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Cleaning data from SportsBook Reviews Online and inserting to MySQL
# ==============================================================================

from os.path import abspath, dirname
import sys
import mysql.connector

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Sbro_Cleaner:
    def __init__(self):
        self.mydb = mysql.connector.connect(host="localhost", user="Dillon",
                                            password='QBface14$', database="sports_betting")
        self.cursor = self.mydb.cursor()

    def table_exists(self):  # Top Level
        """
        checking if table SBRO exists in MySQL
        """
        sql = "SELECT * FROM information_schema.tables WHERE table_name = 'SBRO';"
        self.cursor.execute(sql)
        tables = [table for table in self.cursor]
        # * must find one table with name 'SBRO'
        return (len(tables) == 1) and (tables[0][2] == 'SBRO')

    def create_sql_table(self):  # Top Level
        """
        creating the SQL table
        """
        vc = "VARCHAR(255)"
        dbl = "DOUBLE"
        i = "INT"
        sql = f"""CREATE TABLE SBRO (Season {vc}, Date DATE, Home {vc}, Away {vc},
                Is_Neutral BOOL, OU_Open {dbl}, OU_Open_ML {i}, OU_Close {dbl}, OU_Close_ML {i},
                OU_2H {i}, OU_2H_ML {i}, Home_Line_Open {dbl}, Home_Line_Open_ML {i},
                Away_Line_Open {dbl}, Away_Line_Open_ML {i}, Home_Line_Close {dbl},
                Home_Line_Close_ML {i}, Away_Line_Close {dbl}, Away_Line_Close_ML {i},
                Home_Line_2H {dbl}, Home_Line_2H_ML {i}, Away_Line_2H {dbl}, Away_Line_2H_ML {i},
                Home_ML {i}, Away_ML {i});"""
        self.cursor.execute(sql)

    def run(self):  # Run
        if not self.table_exists():
            self.create_sql_table()


if __name__ == '__main__':
    x = Sbro_Cleaner()
    self = x
    x.run()
