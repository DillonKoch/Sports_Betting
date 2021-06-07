# ==============================================================================
# File: odds_merge_league_data_test.py
# Project: Tests
# File Created: Sunday, 25th October 2020 1:21:43 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 30th October 2020 8:40:55 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# test suite for merge_league_data.py
# ==============================================================================

import datetime
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Odds.merge_league_data import Merge_League_Data, Odds_Game


def test_odds_game_setup():
    game = Odds_Game()
    game_dict = game.__dict__

    attributes = ['Home', 'Away', 'Date', 'Season', 'Is_neutral', 'Home_1Q', 'Home_2Q', 'Home_3Q', 'Home_4Q', 'Home_1H',
                  'Home_2H', 'Home_OT', 'Home_Final', 'Away_1Q', 'Away_2Q', 'Away_3Q', 'Away_4Q', 'Away_1H', 'Away_2H',
                  'Away_OT', 'Away_Final', 'OU_Open', 'OU_Close', 'OU_2H', 'Home_Spread_Open', 'Home_Spread_Close',
                  'Home_Spread_2H', 'Away_Spread_Open', 'Away_Spread_Close', 'Away_Spread_2H', 'Home_ML', 'Away_ML']
    assert list(game_dict.keys()) == attributes
    assert list(game_dict.values()) == [None] * len(attributes)


def test_odds_game_calculate_overtime_ncaab():  # Top Level
    game = Odds_Game()
    game.Home_Final = 100
    game.Home_1H = 45
    game.Home_2H = 45

    game.Away_Final = 99
    game.Away_1H = 52
    game.Away_2H = 45

    assert game.Home_OT is None
    assert game.Away_OT is None
    game.calculate_overtimes("NCAAB")
    assert game.Home_OT == 10
    assert game.Away_OT == 2


def test_odds_game_calculate_overtime_non_ncaab():  # Top Level
    game = Odds_Game()
    game.Home_Final = 44
    game.Home_1Q = 14
    game.Home_2Q = 10
    game.Home_3Q = 14
    game.Home_4Q = 3

    game.Away_Final = 41
    game.Away_1Q = 7
    game.Away_2Q = 13
    game.Away_3Q = 14
    game.Away_4Q = 7

    assert game.Home_OT is None
    assert game.Away_OT is None
    league = np.random.choice(['NFL', 'NCAAF', 'NBA'])
    game.calculate_overtimes(league)
    assert game.Home_OT == 3
    assert game.Away_OT == 0


def test_odds_game_to_row():  # Run
    game = Odds_Game()
    row = game.to_row()
    assert isinstance(row, list)
    assert len(row) == 32
    assert row == [None] * 32


@pytest.fixture  # Fixture
def leagues():
    return ['NFL', 'NBA', 'NCAAF', 'NCAAB']


@pytest.fixture  # Fixture
def mld():
    return Merge_League_Data()


def test_load_data(mld, leagues):  # Top Level
    ncaab_cols = ['Date', 'Rot', 'VH', 'Team', '1st', '2nd', 'Final',
                  'Open', 'Close', 'ML', '2H', 'Season', 'datetime']
    non_ncaab_cols = ['Date', 'Rot', 'VH', 'Team', '1st', '2nd', '3rd', '4th', 'Final',
                      'Open', 'Close', 'ML', '2H', 'Season', 'datetime']

    for league in leagues:
        cols = ncaab_cols if league == 'NCAAB' else non_ncaab_cols
        df = mld.load_data(league)
        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == cols

        # asserting index was reset
        assert len(list(df.index)) == len(set(list(df.index)))


@pytest.fixture  # Fixture
def test_df():
    df = pd.DataFrame({"Open": ["NL", 2, "PK"],
                       "Close": [1, "3-109", 3],
                       "ML": ['pk', 40, 3],
                       "2H": [1, 1, "6-111"]})
    return df


def test_clean_pks(mld, test_df):  # Specific Helper clean_data
    test_df = mld._clean_spread_mls(test_df)
    test_df = mld._clean_no_lines(test_df)
    with pytest.raises(ValueError):
        test_df.astype(float)

    test_df = mld._clean_pks(test_df)
    test_df.astype(float)


def test_clean_spread_mls(mld, test_df):  # Specific Helper clean_data
    test_df = mld._clean_pks(test_df)
    test_df = mld._clean_no_lines(test_df)
    with pytest.raises(ValueError):
        test_df.astype(float)

    test_df = mld._clean_spread_mls(test_df)
    test_df.astype(float)


def test_clean_no_lines(mld, test_df):  # Specific Helper clean_data
    test_df = mld._clean_pks(test_df)
    test_df = mld._clean_spread_mls(test_df)

    with pytest.raises(ValueError):
        test_df.astype(float)

    test_df = mld._clean_no_lines(test_df)
    test_df.astype(float)


def test_clean_data(mld, test_df):  # Top Level
    clean_df = mld.clean_data(test_df)
    clean_df.astype(float)


def test_create_df(mld):  # Top Level
    df = mld.create_df()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0
    assert len(list(df.columns)) == 32


@pytest.fixture  # Fixture
def row_pairs(mld, leagues):
    row_pairs = []
    for league in leagues:
        df = mld.load_data(league)
        df = mld.clean_data(df)

        for i in range(min(100, len(df))):
            if i % 2 == 0:
                row_1 = df.iloc[i, :]
            else:
                row_2 = df.iloc[i, :]
                row_pairs.append([row_1, row_2])
    return row_pairs


def test_add_one_liners(mld, row_pairs):  # Helping Helper
    for row_pair in row_pairs:
        row_1, row_2 = row_pair
        home_row = row_1 if row_1['VH'] in ["N", "H"] else row_2
        away_row = row_1 if row_1['VH'] not in ["N", "H"] else row_2

        game = Odds_Game()
        game = mld._add_one_liners(game, home_row, away_row)

        assert game.Home == home_row['Team']
        assert game.Away == away_row['Team']
        assert game.Date == home_row['datetime']
        assert game.Date == away_row['datetime']
        if not ((np.isnan(game.Home_ML)) and (np.isnan(home_row['ML']))):
            assert game.Home_ML == home_row['ML']
        if not ((np.isnan(game.Away_ML)) and (np.isnan(away_row['ML']))):
            assert game.Away_ML == away_row['ML']


def test_add_scores(mld, row_pairs):  # Helping Helper
    for row_pair in row_pairs:
        row_1, row_2 = row_pair
        home_row = row_1 if row_1['VH'] in ["N", "H"] else row_2
        away_row = row_1 if row_1['VH'] not in ["N", "H"] else row_2

        game = Odds_Game()
        league = "NCAAB" if len(home_row) == 13 else "NFL"
        game = mld._add_scores(game, home_row, away_row, league)

        if league == "NCAAB":
            assert game.Home_1H == home_row['1st']
            assert game.Home_2H == home_row['2nd']
            assert game.Away_1H == away_row['1st']
            assert game.Away_2H == away_row['2nd']
        else:
            assert game.Home_1Q == home_row['1st']
            assert game.Home_2Q == home_row['2nd']
            assert game.Home_3Q == home_row['3rd']
            assert game.Home_4Q == home_row['4th']
            assert game.Away_1Q == away_row['1st']
            assert game.Away_2Q == away_row['2nd']
            assert game.Away_3Q == away_row['3rd']
            assert game.Away_4Q == away_row['4th']

        assert game.Home_Final == home_row['Final']
        assert game.Away_Final == away_row['Final']


def test_get_spread_ou(mld, row_pairs):  # Helping Helper
    for row_pair in row_pairs:
        row_1, row_2 = row_pair
        home_row = row_1 if row_1['VH'] in ["N", "H"] else row_2
        away_row = row_1 if row_1['VH'] not in ["N", "H"] else row_2

        league = "NCAAB" if len(home_row) == 13 else "NFL"
        for col in ['Open', 'Close', '2H']:
            ou_val, home_spread, away_spread = mld._get_spread_ou(home_row, away_row, col, league)
            # all vals are floats or None
            assert ((isinstance(ou_val, float)) or (ou_val is None))
            assert ((isinstance(home_spread, float)) or (home_spread is None))
            assert ((isinstance(away_spread, float)) or (away_spread is None))

            # home/away spreads match up
            assert isinstance(home_spread, type(away_spread))
            if (isinstance(home_spread, float) and (isinstance(away_spread, float))):
                assert home_spread == (away_spread * -1)


def test_create_odds_game(mld, row_pairs):  # Specific Helper
    for row_pair in row_pairs:
        row_1, row_2 = row_pair
        league = "NCAAB" if len(row_1) == 13 else "NFL"
        game = mld._create_odds_game(row_1, row_2, league)
        assert game.Season >= 2007
        assert isinstance(game.Is_neutral, bool)


def test_populate_df(mld, leagues):  # Top Level
    for league in leagues:
        odds_df = mld.load_data(league)
        odds_df = mld.clean_data(odds_df)
        odds_df = odds_df.iloc[:100, :]
        new_df = mld.create_df()
        new_df = mld.populate_df(odds_df, new_df, league)

        assert isinstance(new_df, pd.DataFrame)
        assert len(new_df) == 50
        assert len(new_df.columns) == 32
