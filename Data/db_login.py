# ==============================================================================
# File: db_login.py
# Project: allison
# File Created: Saturday, 19th November 2022 9:52:30 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 19th November 2022 9:52:30 pm
# Modified By: Dillon Koch
# -----
#
# -----
# keeping database login code here
# ==============================================================================

import mysql.connector


def db_cursor():
    mydb = mysql.connector.connect(host='localhost', user='Dillon', password='password', use_pure=True)
    cursor = mydb.cursor()
    return mydb, cursor
