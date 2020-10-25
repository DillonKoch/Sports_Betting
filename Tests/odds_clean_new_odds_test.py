# ==============================================================================
# File: odds_clean_new_odds_test.py
# Project: Tests
# File Created: Saturday, 24th October 2020 8:22:42 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 24th October 2020 10:20:01 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# test suite for Odds/clean_new_odds.py
# ==============================================================================


import datetime
import os
import sys
from os.path import abspath, dirname

import pandas as pd
import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Odds.clean_new_odds import Clean_New_Odds


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


@pytest.fixture(scope='session')  # Fixture
def clean_new_odds():
    return Clean_New_Odds()


@pytest.fixture(scope='session')  # Fixture
def leagues():
    return ['NFL', 'NBA', 'NCAAF', 'NCAAB']


@pytest.fixture(scope='session')  # Fixture
def all_dfs(clean_new_odds, leagues):
    dfs = []
    ncaab_dfs = []
    for league in leagues:
        xlsx_paths = clean_new_odds.load_xlsx_paths(league)
        for path in xlsx_paths:
            df = clean_new_odds.load_df(path)

            if league == 'NCAAB':
                ncaab_dfs.append(df)
            else:
                dfs.append(df)
    return dfs, ncaab_dfs


def test_load_xlsx_paths(clean_new_odds, leagues):  # Top Level
    for league in leagues:
        xlsx_files = clean_new_odds.load_xlsx_paths(league)
        assert isinstance(xlsx_files, list)
        for file in xlsx_files:
            assert isinstance(file, str)
            assert os.path.isfile(file)
            assert file[-5:] == '.xlsx'
            assert league in file


def test_load_df(clean_new_odds, leagues, all_dfs):  # Top Level
    df_cols = ['Date', 'Rot', 'VH', 'Team', '1st', '2nd', '3rd', '4th',
               'Final', 'Open', 'Close', 'ML', '2H']
    ncaab_cols = ['Date', 'Rot', 'VH', 'Team', '1st', '2nd',
                  'Final', 'Open', 'Close', 'ML', '2H']

    dfs, ncaab_dfs = all_dfs
    for df in dfs:
        assert list(df.columns) == df_cols
    for df in ncaab_dfs:
        assert list(df.columns) == ncaab_cols

    for df in dfs + ncaab_dfs:
        assert isinstance(df, pd.DataFrame)
        assert len(df) > 0


def test_add_season_col(clean_new_odds, leagues):  # Top Level
    for league in leagues:
        df_paths = clean_new_odds.load_xlsx_paths(league)
        for df_path in df_paths:
            df = clean_new_odds.load_df(df_path)
            assert 'Season' not in list(df.columns)
            df = clean_new_odds.add_season_col(df, df_path)
            assert 'Season' in list(df.columns)

            seasons = list(df['Season'])
            assert len(set(seasons)) == 1
            assert seasons[0] == df_path.split('.')[0][-7:-3]


def test_datetime_years(clean_new_odds, all_dfs):  # Specific Helper
    dfs, ncaab_dfs = all_dfs
    test_df_path = "not_a_real_path_2015-16.xlsx"
    for df in dfs + ncaab_dfs:
        date_strs = [str(item) for item in list(df['Date'])]
        years = clean_new_odds._datetime_years(date_strs, test_df_path)

        assert isinstance(years, list)
        assert len(set(years)) == 2
        for year in years:
            assert isinstance(year, int)
            assert year in [2015, 2016]


def test_add_datetime_col(clean_new_odds, leagues):  # Top Level
    for league in leagues:
        df_paths = clean_new_odds.load_xlsx_paths(league)
        for df_path in df_paths:
            df = clean_new_odds.load_df(df_path)

            assert 'datetime' not in list(df.columns)
            df = clean_new_odds.add_datetime_col(df, df_path)
            assert 'datetime' in list(df.columns)

            datetimes = list(df['datetime'])
            for dt in datetimes:
                assert isinstance(dt, datetime.datetime)
