# ==============================================================================
# File: model_parent.py
# Project: Modeling
# File Created: Saturday, 12th September 2020 8:03:56 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 12th September 2020 8:08:47 pm
# Modified By: Dillon Koch
# -----
#
# -----
# parent class for creating models that includes helpful functions
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.sqlite_util import Sqlite_util


class Model_Parent:
    def __init__(self, league):
        self.league = league
        self.sql_file_path = ROOT_PATH + f"/SQL/{league}.sql"

    def load_data(self):  # Run
        """
        loads the league's SQL file and performs the query in the sqlite database
        """
        sql = open(self.sql_file_path).read()
        conn, cursor = Sqlite_util().connect_to_db()
        df = pd.read_sql_query(sql, conn)
        return df

    def run(self):  # Run
        pass


if __name__ == '__main__':
    x = Model_Parent("NFL")
    self = x
    x.run()
