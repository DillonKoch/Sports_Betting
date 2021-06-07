# ==============================================================================
# File: esb_data_qa_test.py
# Project: Tests
# File Created: Thursday, 15th October 2020 3:46:22 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 17th October 2020 7:02:31 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Data quality test suite for Elite Sportsbook scraped data
# ==============================================================================


import re
import datetime
import sys
from os.path import abspath, dirname

import pandas as pd
import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def _assert_df_col_type(df, col_name, expected_type, allow_nan=False):  # Global Helper
    if allow_nan:
        df = df.loc[df[col_name].notnull()]

    vals = list(df[col_name])
    for val in vals:
        assert isinstance(val, expected_type)


@pytest.fixture  # Fixture
def leagues():
    return ["NFL", "NBA", "NCAAF", "NCAAB"]


@pytest.fixture  # Fixture
def futures_dfs(leagues):
    futures_dfs = []
    for league in leagues:
        path = ROOT_PATH + f"/ESB/Data/{league}/Futures.csv"
        df = pd.read_csv(path)
        futures_dfs.append(df)
    return futures_dfs


@pytest.mark.qa
def test_futures_dfs_type(futures_dfs):  # QA Testing
    for df in futures_dfs:
        assert isinstance(df, pd.DataFrame)


@pytest.mark.qa
def test_futures_dfs_col_names(futures_dfs):  # QA Testing
    true_cols = ['Title', 'Description', 'Bet', 'Odds', 'scraped_ts']
    for df in futures_dfs:
        cols = list(df.columns)
        assert cols == true_cols


@pytest.mark.qa
def test_futures_dfs_col_types(futures_dfs):  # QA Testing
    for df in futures_dfs:
        _assert_df_col_type(df, "Title", str)
        _assert_df_col_type(df, "Description", str, allow_nan=True)
        _assert_df_col_type(df, "Bet", str)

        df['Odds'] = df['Odds'].astype(float)
        _assert_df_col_type(df, "Odds", float)

        df['scraped_ts'] = pd.to_datetime(df['scraped_ts'])
        _assert_df_col_type(df, "scraped_ts", datetime.datetime)


@pytest.mark.qa
def test_futures_dfs_no_newlines_tabs(futures_dfs):  # QA Testing
    for df in futures_dfs:
        str_cols = ['Title', 'Description', 'Bet']
        for col in str_cols:
            vals = list(df[col].astype(str))
            for val in vals:
                assert '\n' not in val
                assert '\t' not in val


@pytest.mark.qa
def test_futures_dfs_scrape_ts_sorted(futures_dfs):  # QA Testing
    for df in futures_dfs:
        scrape_ts_vals = list(df['scraped_ts'])
        sorted_ts_vals = sorted(scrape_ts_vals)
        assert scrape_ts_vals == sorted_ts_vals


@pytest.fixture  # Fixture
def game_lines_dfs(leagues):
    dfs = []
    for league in leagues:
        path = ROOT_PATH + f"/ESB/Data/{league}/Game_Lines.csv"
        df = pd.read_csv(path)
        dfs.append(df)
    return dfs


@pytest.fixture  # Fixture
def game_line_float_cols():
    float_cols = ['Over_ESB', 'Over_ml_ESB', 'Under_ESB', 'Under_ml_ESB',
                  'Home_Line_ESB', 'Home_Line_ml_ESB', 'Away_Line_ESB', 'Away_Line_ml_ESB',
                  'Home_ML_ESB', 'Away_ML_ESB']
    return float_cols


@pytest.mark.qa
def test_game_lines_dfs_type(game_lines_dfs):  # QA Testing
    for df in game_lines_dfs:
        assert isinstance(df, pd.DataFrame)


@pytest.mark.qa
def test_game_lines_dfs_col_names(game_lines_dfs):  # QA Testing
    true_cols = ['Title', 'datetime', 'Game_Time', 'Home', 'Away', 'Over_ESB', 'Over_ml_ESB',
                 'Under_ESB', 'Under_ml_ESB', 'Home_Line_ESB', 'Home_Line_ml_ESB',
                 'Away_Line_ESB', 'Away_Line_ml_ESB', 'Home_ML_ESB', 'Away_ML_ESB', 'scraped_ts']

    for df in game_lines_dfs:
        cols = list(df.columns)
        assert true_cols == cols


@pytest.mark.qa
def test_game_lines_dfs_col_types(game_lines_dfs, game_line_float_cols):  # QA Testing
    for df in game_lines_dfs:

        # load float cols as floats
        for col in game_line_float_cols:
            df[col] = df[col].astype(float)

        # load datetime cols in datetime type
        dt_cols = ['datetime', 'scraped_ts']
        for col in dt_cols:
            df[col] = pd.to_datetime(df[col])

        _assert_df_col_type(df, 'Title', str)
        _assert_df_col_type(df, 'datetime', datetime.datetime)
        _assert_df_col_type(df, 'Game_Time', str)
        _assert_df_col_type(df, 'Home', str)  # FIXME must be valid team
        _assert_df_col_type(df, 'Away', str)
        _assert_df_col_type(df, 'Over_ESB', float)
        _assert_df_col_type(df, 'Over_ml_ESB', float)
        _assert_df_col_type(df, 'Under_ESB', float)
        _assert_df_col_type(df, 'Under_ml_ESB', float)
        _assert_df_col_type(df, 'Home_Line_ESB', float)
        _assert_df_col_type(df, 'Home_Line_ml_ESB', float)
        _assert_df_col_type(df, 'Away_Line_ESB', float)
        _assert_df_col_type(df, 'Away_Line_ml_ESB', float)
        _assert_df_col_type(df, 'Home_ML_ESB', float)
        _assert_df_col_type(df, 'Away_ML_ESB', float)
        _assert_df_col_type(df, 'scraped_ts', datetime.datetime)


@pytest.mark.qa
def test_game_lines_dfs_game_time_regex(game_lines_dfs):  # QA Testing
    """
    asserts that the Game_Time column always matches the regex below
    00:00 CDT (or CST)
    """
    gt_comp = re.compile(r"\d{2}:\d{2} C(S|D)T")
    for df in game_lines_dfs:
        game_times = list(df['Game_Time'])
        for gt in game_times:
            match = re.search(gt_comp, gt)
            assert match is not None


@pytest.mark.qa
def test_game_lines_dfs_scrape_ts_sorted(game_lines_dfs):  # QA Testing
    for df in game_lines_dfs:
        scrape_ts_vals = list(df['scraped_ts'])
        sorted_ts_vals = sorted(scrape_ts_vals)
        assert scrape_ts_vals == sorted_ts_vals


@pytest.fixture  # Fixture
def game_prop_dfs(leagues):
    dfs = []
    for league in leagues:
        path = ROOT_PATH + f"/ESB/Data/{league}/Game_Props.csv"
        df = pd.read_csv(path)
        dfs.append(df)
    return dfs


@pytest.fixture  # Fixture
def game_prop_str_cols():
    return ['Game_Time', 'Home', 'Away', 'Title', 'Description', 'Bet']


@pytest.mark.qa
def test_game_prop_dfs_type(game_prop_dfs):  # QA Testing
    for df in game_prop_dfs:
        assert isinstance(df, pd.DataFrame)


@pytest.mark.qa
def test_game_prop_dfs_col_names(game_prop_dfs):  # QA Testing
    true_cols = ['datetime', 'Game_Time', 'Home', 'Away', 'Title', 'Description',
                 'Bet', 'Spread/overunder', 'Odds', 'scraped_ts']
    for df in game_prop_dfs:
        cols = list(df.columns)
        assert cols == true_cols


@pytest.mark.qa
def test_game_prop_dfs_col_types(game_prop_dfs):  # QA Testing
    str_cols = ['Game_Time', 'Home', 'Away', 'Title', 'Description', 'Bet']
    float_cols = ['Spread/overunder', 'Odds']
    dt_cols = ['datetime', 'scraped_ts']
    for df in game_prop_dfs:

        for col in str_cols:
            _assert_df_col_type(df, col, str)

        for col in float_cols:
            df[col] = df[col].astype(float)
            _assert_df_col_type(df, col, float)

        for col in dt_cols:
            df[col] = pd.to_datetime(df[col])
            _assert_df_col_type(df, col, datetime.datetime)


@pytest.mark.qa
def test_game_props_dfs_scrape_ts_sorted(game_prop_dfs):  # QA Testing
    for df in game_prop_dfs:
        scrape_ts_vals = list(df['scraped_ts'])
        sorted_ts_vals = sorted(scrape_ts_vals)
        assert scrape_ts_vals == sorted_ts_vals


@pytest.mark.qa
def test_game_props_dfs_game_time_regex(game_prop_dfs):  # QA Testing
    """
    asserts that the Game_Time column always matches the regex below
    00:00 CDT (or CST)
    """
    gt_comp = re.compile(r"\d{2}:\d{2} C(S|D)T")
    for df in game_prop_dfs:
        game_times = list(df['Game_Time'])
        for gt in game_times:
            match = re.search(gt_comp, gt)
            assert match is not None
