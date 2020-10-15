# ==============================================================================
# File: esb_data_qa_test.py
# Project: Tests
# File Created: Thursday, 15th October 2020 3:46:22 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 15th October 2020 4:34:47 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Data quality test suite for Elite Sportsbook scraped data
# ==============================================================================


import datetime
import sys
from os.path import abspath, dirname

import pandas as pd
import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


@pytest.fixture
def leagues():
    return ["NFL", "NBA", "NCAAF", "NCAAB"]


@pytest.fixture
def futures_dfs(leagues):
    futures_dfs = []
    for league in leagues:
        path = ROOT_PATH + f"/ESB/Data/{league}/Futures.csv"
        df = pd.read_csv(path)
        futures_dfs.append(df)
    return futures_dfs


def _assert_df_col_type(df, col_name, expected_type, allow_nan=False):  # Specific Helper
    if allow_nan:
        df = df.loc[df[col_name].notnull()]

    vals = list(df[col_name])
    for val in vals:
        assert isinstance(val, expected_type)


def test_futures_dfs_qa(futures_dfs):  # QA Testing
    for df in futures_dfs:
        assert isinstance(df, pd.DataFrame)

        # columns match
        cols = list(df.columns)
        true_cols = ['Title', 'Description', 'Bet', 'Odds', 'scraped_ts']
        assert cols == true_cols

        # asserting column types
        _assert_df_col_type(df, "Title", str)
        _assert_df_col_type(df, "Description", str, allow_nan=True)
        _assert_df_col_type(df, "Bet", str)

        df['Odds'] = df['Odds'].astype(float)
        _assert_df_col_type(df, "Odds", float)

        df['scraped_ts'] = pd.to_datetime(df['scraped_ts'])
        _assert_df_col_type(df, "scraped_ts", datetime.datetime)

        # new format
        # new_df = df[date > some_date]
        # now assert no nulls


def game_lines_dfs_qa():
    pass


def game_props_dfs_qa():
    pass
