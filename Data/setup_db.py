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
        building Sportsbook Reviews Online table in database
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
                Home_ML {i}, Away_ML {i},
                PRIMARY KEY (Date, Home, Away));"""
        self.cursor.execute(sql)

    def create_covers(self, tables, league):  # Top Level
        """
        building Covers Injury table in database
        """
        if f"Covers_{league}" in tables:
            return None

        print("Creating Covers Table...")
        vc = "VARCHAR(255)"
        i = "INT"
        sql = f"""CREATE TABLE Covers_{league} (Player_ID {i}, Status_Date DATE, Team {vc}, Player {vc},
                  Position {vc}, Status {vc}, Description {vc}, scraped_ts DATE,
                  PRIMARY KEY (Player_ID, Status_Date));"""
        self.cursor.execute(sql)

    def create_esb(self, tables, league):  # Top Level
        """
        building Elite Sportsbook Game Lines table in database
        """
        if f"ESB_{league}" in tables:
            return None

        print("Creating Elite Sportsbook Table...")
        vc = "VARCHAR(255)"
        i = "INT"
        dbl = "DOUBLE"
        sql = f"""CREATE TABLE ESB_{league} (Date DATE, Home {vc}, Away {vc},
                  Over_Odds {dbl}, Over_ML {i}, Under_Odds {dbl}, Under_ML {i}, Home_Spread {dbl},
                  Home_Spread_ML {i}, Away_Spread {dbl}, Away_Spread_ML {dbl}, Home_ML {i},
                  Away_ML {i}, scraped_ts DATE,
                  PRIMARY KEY (Date, Home, Away));"""
        self.cursor.execute(sql)

    def create_espn_games(self, tables, league):  # Top Level
        if f"ESPN_Games_{league}" in tables:
            return None

        print("Creating ESPN Games Table...")
        vc = "VARCHAR(255)"
        i = "INT"
        dbl = "DOUBLE"
        football_sql = f"""CREATE TABLE ESPN_Games_{league} (Game_ID {i}, Season {vc}, Week {vc},
                  Date DATE, Home {vc}, Away {vc}, Home_Record {vc}, Away_Record {vc},
                  Network {vc}, Final_Status {vc}, H1H {i}, H2H {i}, H1Q {i}, H2Q {i},
                  H3Q {i}, H4Q {i}, HOT {i}, A1H {i}, A2H {i}, A1Q {i}, A2Q {i}, A3Q {i},
                  A4Q {i}, AOT {i}, Home_Final {i}, Away_Final {i}, Home_1st_Downs {i},
                  Away_1st_Downs {i}, Home_Passing_1st_Downs {i}, Away_Passing_1st_Downs {i},
                  Home_Rushing_1st_Downs {i}, Away_Rushing_1st_Downs {i},
                  Home_1st_Downs_From_Penalties {i}, Away_1st_Downs_From_Penalties {i},
                  Home_3rd_Down_Efficiency {dbl}, Away_3rd_Down_Efficiency {dbl},
                  Home_4th_Down_Efficiency {dbl}, Away_4th_Down_Efficiency {dbl},
                  Home_Total_Plays {i}, Away_Total_Plays {i}, Home_Total_Yards {i},
                  Away_Total_Yards {i}, Home_Total_Drives {i}, Away_Total_Drives {i},
                  Home_Yards_Per_Play {dbl}, Away_Yards_Per_Play {dbl}, Home_Passing {i},
                  Away_Passing {i}, Home_Comp_Att {vc}, Away_Comp_Att {vc},
                  Home_Yards_Per_Pass {dbl}, Away_Yards_Per_Pass {dbl},
                  Home_Interceptions_Thrown {i}, Away_Interceptions_Thrown {i},
                  Home_Sacks_Yards_Lost {vc}, Away_Sacks_Yards_Lost {vc},
                  Home_Rushing {i}, Away_Rushing {i}, Home_Rushing_Attempts {i},
                  Away_Rushing_Attempts {i}, Home_Yards_Per_Rush {dbl},
                  Away_Yards_Per_Rush {dbl}, Home_Red_Zone_Made_Att {vc},
                  Away_Red_Zone_Made_Att {vc}, Home_Penalties {vc}, Away_Penalties {vc},
                  Home_Turnovers {i}, Away_Turnovers {i}, Home_Fumbles_Lost {i},
                  Away_Fumbles_Lost {i}, Home_Defensive_Special_Teams_TDs {i},
                  Away_Defensive_Special_Teams_TDs {i}, Home_Possession {vc}, Away_Possession {vc},
                  PRIMARY KEY (Date, Home, Away));"""

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
            self.create_covers(tables, league)
            self.create_esb(tables, league)
            # TODO more tables


if __name__ == '__main__':
    x = Setup_DB()
    self = x
    x.run()
