# ==============================================================================
# File: test_sbo_clean_data.py
# Project: Tests
# File Created: Saturday, 12th June 2021 10:22:17 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 12th June 2021 10:22:17 pm
# Modified By: Dillon Koch
# -----
#
# -----
# test suite for sbo_clean_data.py
# ==============================================================================

import concurrent.futures
import os
import re
import sys
from os.path import abspath, dirname

import pandas as pd
import pytest
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Scrapers.sbo_clean_data import Sbo_Clean_Data


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def multithread(func, func_args):  # Multithreading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = list(tqdm(executor.map(func, func_args), total=len(func_args)))
    return result


@pytest.fixture(scope='session')  # Fixture
def scd():
    return Sbo_Clean_Data()


@pytest.fixture(scope='session')  # Fixture
def leagues():
    return ['NFL', 'NBA', 'NCAAF', 'NCAAB']


def test_init(scd):  # Top Level  Done
    cols = ["Season", "Date", "Home", "Away", "is_neutral",
            "H1Q", "H2Q", "H3Q", "H4Q", "H1H", "H2H", "HOT", "HFinal",
            "A1Q", "A2Q", "A3Q", "A4Q", "A1H", "A2H", "AOT", "AFinal",
            "OU_Open", "OU_Close", "OU_2H",
            "Home_Spread_Open", "Home_Spread_Close", "Home_Spread_2H",
            "Away_Spread_Open", "Away_Spread_Close", "Away_Spread_2H",
            "Home_ML", "Away_ML"]
    assert list(scd.df_cols) == cols


@pytest.fixture(scope='session')  # Fixture
def path_df_league_combos(leagues):
    """
    list of (df, league) combinations
    """
    path_df_league_combos = []
    for league in leagues:
        paths = listdir_fullpath(ROOT_PATH + f"/Data/Odds/{league}")
        dfs = [pd.read_excel(path) for path in tqdm(paths)]
        path_df_league_combos += [(path, df, league) for path, df in zip(paths, dfs)]
    return path_df_league_combos


def test_df_to_row_pairs(scd, path_df_league_combos):  # Global Helper  Done
    for path_df_league_combo in path_df_league_combos:
        _, df, league = path_df_league_combo
        row_pairs = scd._df_to_row_pairs(df)
        assert isinstance(row_pairs, list)
        for row_pair in row_pairs:
            assert isinstance(row_pair, tuple)
            for row in row_pair:
                assert isinstance(row, list)
                row_len = 11 if league == "NCAAB" else 13
                assert len(row) == row_len


def test_add_season(scd, path_df_league_combos):  # Top Level  Done
    for path_df_league_combo in path_df_league_combos:
        path, df, _ = path_df_league_combo
        # testing # columns
        len_before = len(df.columns)
        df = scd.add_season(df, path)
        assert isinstance(df, pd.DataFrame)
        assert len(df.columns) == (len_before + 1)
        # season is a new col
        assert 'Season' in list(df.columns)
        # season values are valid
        season_vals = list(df['Season'])
        for season_val in season_vals:
            assert re.match(re.compile(r"\d{4}-\d{2}"), season_val)


def test_add_overtime(scd, path_df_league_combos):  # Top Level  Done
    for path_df_league_combo in path_df_league_combos:
        _, df, league = path_df_league_combo
        df = scd.add_overtime(df, league)
        assert isinstance(df, pd.DataFrame)
        assert 'OT' in list(df.columns)
        overtime_vals = list(df['OT'])
        for overtime_val in overtime_vals:
            assert isinstance(overtime_val, (int, float))


def test_add_ml_cols(scd, path_df_league_combos):  # Top Level  Done
    for path_df_league_combo in path_df_league_combos:
        _, df, _ = path_df_league_combo
        df = scd.add_ml_cols(df)
        assert isinstance(df, pd.DataFrame)

        for ml_col in ["Open_ML", "Close_ML", "2H_ML"]:
            assert ml_col in list(df.columns)
            ml_col_vals = list(df[ml_col])

            for ml_col_val in ml_col_vals:
                ml_col_val = float(ml_col_val)
                assert ml_col_val < -100
                assert ml_col_val > -150


def test_reorder_cols(scd, path_df_league_combos):  # Top Level  Done
    col_order = ["Season", "Date", "Rot", "VH", "Team", "1st", "2nd", "3rd", "4th", "OT",
                 "Final", "Open", "Open_ML", "Close", "Close_ML", "ML", "2H", "2H_ML"]

    for path_df_league_combo in path_df_league_combos:
        path, df, league = path_df_league_combo
        col_order = [col for col in col_order if col not in ['3rd', '4th']] if league == "NCAAB" else col_order
        df = scd.add_season(df, path)
        df = scd.add_overtime(df, league)
        df = scd.add_ml_cols(df)
        df = scd.reorder_cols(df, league)
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == col_order


def test_home_away_row(scd):  # Specific Helper
    pass


def test_home_away_info(scd):  # Specific Helper
    pass


def test_score_vals(scd):  # Specific Helper
    pass


def test_open_vals(scd):  # Specific Helper
    pass


def test_line_vals(scd):  # Specific Helper
    pass


def test_2h_vals(scd):  # Specific Helper
    pass


def test_odds_to_clean_df(scd):  # Top Level
    for path_df_league_combo in path_df_league_combos:
        path, df, league = path_df_league_combo
        df = scd.add_season(df, path)
        df = scd.add_overtime(df, league)
        df = scd.add_ml_cols(df)
        df = scd.reorder_cols(df, league)
        df = scd.odds_to_clean_df(df)
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == scd.df_cols


def test_save_full_df(scd):
    pass
