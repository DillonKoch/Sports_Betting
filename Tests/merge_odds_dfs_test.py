# ==============================================================================
# File: merge_odds_dfs_test.py
# Project: Tests
# File Created: Tuesday, 20th October 2020 8:11:07 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 20th October 2020 8:24:17 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Test suite for merge_odds_dfs.py
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd
import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Utility.merge_odds_dfs import merge_odds_dfs


def test_game_props_dfs():
    old_df = pd.read_csv("./test_game_props_full.csv")
    new_df = pd.read_csv("./test_game_props_new.csv")

    drop_cols = ['datetime', 'Game_Time', 'Home', 'Away', 'Title',
                 'Description', 'Bet']
    odds_cols = ['Spread/overunder', 'Odds']

    merged_df = merge_odds_dfs(full_df, new_df, drop_cols, odds_cols)

# ! pick up here with merge odds testing
