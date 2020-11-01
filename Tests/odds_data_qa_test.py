# ==============================================================================
# File: odds_data_qa_test.py
# Project: Tests
# File Created: Saturday, 24th October 2020 8:20:38 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 31st October 2020 1:46:35 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Quality assurance for data in the Odds module
# ==============================================================================


import datetime
import os
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Tests.esb_data_qa_test import _assert_df_col_type


@pytest.fixture(scope='session')
def leagues():
    return ['NFL', 'NBA', 'NCAAF', 'NCAAB']


@pytest.fixture(scope='session')
def dfs(leagues):
    dfs = []
    for league in leagues:
        path = ROOT_PATH + f"/Odds/{league}.csv"
        if os.path.isfile(path):
            df = pd.read_csv(path)
            dfs.append(df)
    return dfs


def test_df_types(dfs):  # QA Testing
    for df in dfs:
        assert isinstance(df, pd.DataFrame)


def test_df_col_names(dfs):  # QA Testing
    cols = ["Season", "datetime", "Home", "Away",
            "H1Q", "H2Q", "H3Q", "H4Q",
            "H1H", "H2H", "HOT", "HFinal",
            "A1Q", "A2Q", "A3Q", "A4Q",
            "A1H", "A2H", "AOT", "AFinal", "IsNeutral",
            "OU_Open", "OU_Close", "OU_2H",
            "Home_Spread_Open", "Home_Spread_Close", "Home_Spread_2H",
            "Away_Spread_Open", "Away_Spread_Close", "Away_Spread_2H",
            "Home_ML", "Away_ML"]
    for df in dfs:
        assert list(df.columns) == cols


def test_df_col_types(dfs, leagues):  # QA Testing
    for df, league in zip(dfs, leagues):

        # cols same for all leagues
        df['Season'] = df['Season'].astype(int)
        _assert_df_col_type(df, 'Season', int)
        _assert_df_col_type(df, 'datetime', str)
        df['datetime'] = pd.to_datetime(df['datetime'])
        _assert_df_col_type(df, 'datetime', datetime.datetime)
        _assert_df_col_type(df, 'Home', str)
        _assert_df_col_type(df, 'Away', str)
        _assert_df_col_type(df, "IsNeutral", int)

        # NCAAB col types
        half_cols = ['H1H', 'H2H', 'A1H', 'A2H']
        allow_half_nan = False if league == "NCAAB" else True
        for half_col in half_cols:
            _assert_df_col_type(df, half_col, int, allow_nan=allow_half_nan)

        # NON NCAAB col types
        quarter_cols = ['H1Q', 'H2Q', 'H3Q', 'H4Q', 'A1Q', 'A2Q', 'A3Q', 'A4Q']
        allow_quarter_nan = True if league == "NCAAB" else False
        for quarter_col in quarter_cols:
            df[quarter_col] = df[quarter_col].astype(float)
            _assert_df_col_type(df, quarter_col, float, allow_nan=allow_quarter_nan)

        # score cols that are same for all leagues
        other_score_cols = ['HOT', 'HFinal', 'AOT', 'AFinal']
        for other_score_col in other_score_cols:
            df[other_score_col] = df[other_score_col].astype(float)
            _assert_df_col_type(df, other_score_col, float)

        # Odds cols
        odds_float_cols = ['OU_Open', 'OU_Close', 'OU_2H',
                           'Home_Spread_Open', 'Home_Spread_Close', 'Home_Spread_2H',
                           'Away_Spread_Open', 'Away_Spread_Close', 'Away_Spread_2H',
                           'Home_ML', 'Away_ML']
        for odds_float_col in odds_float_cols:
            _assert_df_col_type(df, odds_float_col, float, allow_nan=True)


def _test_spread_cols(df, home_col, away_col):
    home_vals = list(df[home_col])
    away_vals = list(df[away_col])
    for home_val, away_val in zip(home_vals, away_vals):
        nan_count = sum([np.isnan(item) for item in [home_val, away_val]])
        assert nan_count != 1
        if nan_count == 0:
            assert (home_val * -1) == away_val


def test_spreads_match(dfs):
    for df in dfs:
        _test_spread_cols(df, "Home_Spread_Open", "Away_Spread_Open")
        _test_spread_cols(df, "Home_Spread_Close", "Away_Spread_Close")
        _test_spread_cols(df, "Home_Spread_2H", "Away_Spread_2H")


def test_null_cols(dfs, leagues):  # TODO
    for df, league in zip(dfs, leagues):
        if league == 'NCAAB':
            # assert q cols null
            pass
        else:
            # assert half cols null
            pass

        never_null_cols = ['Season']
        # add more, assert these^ never null


def test_is_neutral(dfs):  # TODO
    # make sure all 1's and 0's
    pass


def test_ml_vals(dfs):  # TODO
    # make sure negative val further from 0 than positive
    pass


def test_spreads_lessthan_overunders(dfs):  # TODO
    # spread vals should always be less than the O/U val
    pass


def test_scores_add_up(dfs):
    # quarter and overtime scores should add to the final score
    pass
