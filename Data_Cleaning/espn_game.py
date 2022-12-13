# ==============================================================================
# File: espn_game.py
# Project: allison
# File Created: Saturday, 10th December 2022 9:21:08 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 10th December 2022 9:21:09 pm
# Modified By: Dillon Koch
# -----
#
# -----
# cleaning data in ESPN_Games_{league} tables
# ==============================================================================


import sys
from os.path import abspath, dirname

from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Data.db_info import DB_Info
from Data.db_login import db_cursor
from Data.db_ops import DB_Ops


class Clean_ESPN_Game:
    def __init__(self, league):
        self.league = league
        self.db, self.cursor = db_cursor()
        self.cursor.execute("USE sports_betting;")
        self.db_info = DB_Info()
        self.db_ops = DB_Ops()

    def query_table(self):  # Top Level
        """
        querying all data from the ESPN_Games_{league} table
        """
        sql = f"SELECT * FROM ESPN_Games_{self.league} WHERE Home != 'Kennedy Cougars';"
        self.cursor.execute(sql)
        data = [list(item) for item in self.cursor.fetchall()]
        cols = self.db_info.get_cols(f"ESPN_Games_{self.league}")
        return data, cols

    def clean_possession(self, row, update):  # Top Level
        """
        converting posession from min:sec to just total seconds
        """
        home_poss = row[-2]
        away_poss = row[-1]
        if isinstance(home_poss, str) and ':' in home_poss:
            home_poss = (int(home_poss.split(":")[0]) * 60) + int(home_poss.split(":")[1])
            row[-2] = home_poss
            update = True
        if isinstance(away_poss, str) and ':' in away_poss:
            away_poss = (int(away_poss.split(":")[0]) * 60) + int(away_poss.split(":")[1])
            row[-1] = away_poss
            update = True
        return row, update

    def clean_final_status(self, row, update):  # Top Level
        """
        if there are final scores and final_status is None, this updaets it to Final(/OT)
        """
        final_status = row[9]
        if final_status is None:
            if not all(item is None for item in row[24:26]):
                if (row[16] is None) and (row[23] is None):
                    row[9] = 'Final'
                else:
                    row[9] = 'Final/OT'
                update = True
        return row, update

    def run(self):  # Run
        # ! cleaning
        # clean possession to be in seconds
        # clean final status (fill in if appropriate)
        # ! process
        # query all data, go through row by row and update if necessary
        data, cols = self.query_table()
        for row in tqdm(data):
            update = False
            row, update = self.clean_possession(row, update)
            row, update = self.clean_final_status(row, update)

            if update:
                self.db_ops.update_row(f"ESPN_Games_{self.league}", row)


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        x = Clean_ESPN_Game(league)
        self = x
        x.run()
