# ==============================================================================
# File: parent_parser.py
# Project: scrapers
# File Created: Sunday, 16th May 2021 9:27:53 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 16th May 2021 9:27:54 pm
# Modified By: Dillon Koch
# -----
#
# -----
# parent class for parsers
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Parent_Parser:
    def __init__(self):
        pass

    def game_lines_df(self):  # Specific Helper
        """
        creates an empty dataframe for game lines bets
        """
        cols = ['Title', 'Date', 'Time', 'Home', 'Away',
                'Over', 'Over_ML', 'Under', 'Under_ML',
                'Home_Line', 'Home_Line_ML', 'Away_Line', 'Away_Line_ML',
                'Home_ML', 'Away_ML', 'scrape_ts']
        return pd.DataFrame(columns=cols)

    def game_props_df(self):  # Specific Helper
        """
        creates an empty dataframe for game props bets
        """
        cols = ['Date', 'Time', 'Home', 'Away', 'Title', 'Description',
                'Bet', 'Spread/OU', 'Odds', 'scrape_ts']
        return pd.DataFrame(columns=cols)

    def futures_df(self):  # Specific Helper
        """
        creates an empty dataframe for futures bets
        """
        cols = ['Title', 'Description', 'Bet', 'Odds', 'scrape_ts']
        return pd.DataFrame(columns=cols)

    def sort_df(self, df):  # Global Helper
        pass

    def save_df(self, df):  # Top Level
        pass


if __name__ == '__main__':
    x = Parent_Parser()
    self = x
    x.run()
