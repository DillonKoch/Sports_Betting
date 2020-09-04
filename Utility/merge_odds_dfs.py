# ==============================================================================
# File: merge_odds_dfs.py
# Project: Utility
# File Created: Thursday, 3rd September 2020 4:27:12 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 3rd September 2020 8:25:36 pm
# Modified By: Dillon Koch
# -----
#
# -----
# function to merge two dataframes for the same bet, but don't include the same odds
# twice if the new odds are the same as the most recent odds

# the complicated part is that if a game has the Vikings -3.5, then -4.0, then -3.5 again,
# I want to include both -3.5 rows, so a simple pd.drop_duplicates() won't work
# ==============================================================================

import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


drop_cols = ['datetime', 'Home', "Away"]


def _split_old_df(old_df, drop_cols):
    """
    splits the old_df into two dfs, the locked_df that has duplicated rows,
    and newest_df that is the newest row for each combo of drop_cols
    """
    mask = old_df.duplicated(subset=drop_cols, keep='last')
    locked_df = old_df.loc[mask]
    newest_df = old_df.loc[~mask]
    return locked_df, newest_df


def merge_odds_dfs(old_df, new_df, drop_cols, odds_cols):
    """
    merges an old odds df with a new df, adding the new rows from new_df that have new bets
    since the most recent old_df row for that game (or adding the first row of a new game)
    """
    assert list(old_df.columns) == list(new_df.columns)

    locked_df, newest_df = _split_old_df(old_df, drop_cols)
    combined_newest = pd.concat([newest_df, new_df])
    combined_newest.reset_index(inplace=True, drop=True)
    combined_newest.drop_duplicates(subset=odds_cols, inplace=True)

    full_df = pd.concat([locked_df, combined_newest])
    full_df.reset_index(inplace=True, drop=True)
    return full_df
