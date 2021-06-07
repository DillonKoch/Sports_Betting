# ==============================================================================
# File: merge_odds_dfs_test.py
# Project: Tests
# File Created: Tuesday, 20th October 2020 8:11:07 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 21st October 2020 8:03:22 pm
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

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Utility.merge_odds_dfs import merge_odds_dfs


def test_game_props_dfs():
    old_df = pd.read_csv(ROOT_PATH + "/Tests/data/test_game_props_old.csv")
    new_df = pd.read_csv(ROOT_PATH + "/Tests/data/test_game_props_new.csv")
    merged_df_csv = pd.read_csv(ROOT_PATH + '/Tests/data/test_game_props_merged.csv')

    drop_cols = ['datetime', 'Game_Time', 'Home', 'Away', 'Title',
                 'Description', 'Bet']
    # odds_cols = ['Spread/overunder', 'Odds']

    merged_df = merge_odds_dfs(old_df, new_df, drop_cols)
    assert len(merged_df) == 4
    assert merged_df_csv.equals(merged_df)


def test_game_lines_dfs():
    old_df = pd.read_csv(ROOT_PATH + "/Tests/data/test_game_lines_old.csv")
    new_df = pd.read_csv(ROOT_PATH + "/Tests/data/test_game_lines_new.csv")
    merged_df_csv = pd.read_csv(ROOT_PATH + '/Tests/data/test_game_lines_merged.csv')

    drop_cols = ['Title', 'datetime', 'Game_Time', 'Home', 'Away']
    # odds_cols = ['Over_ESB', 'Over_ml_ESB', 'Under_ESB', 'Under_ml_ESB',
    #              'Home_Line_ESB', 'Home_Line_ml_ESB', 'Away_Line_ESB', 'Away_Line_ml_ESB',
    #              'Home_ML_ESB', 'Away_ML_ESB']

    merged_df = merge_odds_dfs(old_df, new_df, drop_cols)
    assert len(merged_df) == 5
    assert merged_df_csv.equals(merged_df)
