# ==============================================================================
# File: cleaning_funcs.py
# Project: Utility
# File Created: Saturday, 4th July 2020 2:32:02 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 4th July 2020 2:35:21 pm
# Modified By: Dillon Koch
# -----
#
# -----
# functions for cleaning dataframes
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility import listdir_fullpath


def replace_espn_team_name(self, league, old_name, new_name):
    league_paths = listdir_fullpath(ROOT_PATH + "/ESPN_Data/NCAAF/")
    league_dfs = [pd.read_csv(path) for path in league_paths]

    for path, df in zip(league_paths, league_dfs):
        df = df.replace(old_name, new_name)
        df.to_csv(path, index=False)
    print("DONE!")
