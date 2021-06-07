# ==============================================================================
# File: sqlite_util_test.py
# Project: Tests
# File Created: Saturday, 22nd August 2020 1:13:20 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 22nd August 2020 1:21:45 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Testing sqlite_util.py file
# ==============================================================================


import sqlite3
import sys
from os.path import abspath, dirname
from unittest import TestCase


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.sqlite_util import Sqlite_util


class Test_Sqlite_util(TestCase):

    def setUp(self):
        pass

    def test_connect_to_db(self):
        s = Sqlite_util()
        conn, cursor = s.connect_to_db()

        self.assertIsInstance(conn, sqlite3.Connection)
        self.assertIsInstance(cursor, sqlite3.Cursor)

    def test_insert_df(self):
        pass
