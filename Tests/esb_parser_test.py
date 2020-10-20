# ==============================================================================
# File: esb_parser_test.py
# Project: Tests
# File Created: Saturday, 17th October 2020 9:19:51 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 19th October 2020 8:43:02 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Test suite for esb_parser.py
# ==============================================================================


import datetime
import pickle
import re
import sys
from os.path import abspath, dirname

import bs4
import pandas as pd
import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from ESB.esb_parser import ESB_Parser


@pytest.fixture(scope='session')  # Fixture
def parser():
    return ESB_Parser()


@pytest.fixture(scope='session')  # Fixture
def sps():
    with open(ROOT_PATH + "/Tests/esb_sps.pickle", "rb") as f:
        sps = pickle.load(f)
    return [item[1] for item in sps]


@pytest.fixture(scope='session')  # Fixture
def game_lines_sps(parser, sps):
    return [sp for sp in sps if parser.detect_bet_type(sp) == 'Game_Lines']


@pytest.fixture(scope='session')  # Fixture
def game_lines_events(parser, game_lines_sps):
    events = []
    for sp in game_lines_sps:
        date_events = parser._get_date_events(sp)

        date = None
        for date_event in date_events:
            date, found_date = parser._check_is_date(date_event, date)
            if not found_date:
                events.append(date_event)
    return events


@pytest.fixture(scope='session')  # Fixture
def game_props_sps(parser, sps):
    return [sp for sp in sps if parser.detect_bet_type(sp) == 'Game_Props']


@pytest.fixture(scope='session')  # Fixture
def game_props_events(parser, game_props_sps):
    events = []
    for sp in game_props_sps:
        date_events = parser._get_date_events(sp)

        date = None
        for date_event in date_events:
            date, found_date = parser._check_is_date(date_event, date)
            if not found_date:
                events.append(date_event)
    return events


@pytest.fixture(scope='session')  # Fixture
def futures_sps(parser, sps):
    return [sp for sp in sps if parser.detect_bet_type(sp) == 'Futures']


def test_get_scrape_ts(parser):  # Global Helper
    start_time = datetime.datetime.now().replace(second=0, microsecond=0)
    scrape_ts = parser._get_scrape_ts()
    assert isinstance(scrape_ts, str)

    scrape_dt = datetime.datetime.strptime(scrape_ts, "%Y-%m-%d %H:%M")
    assert isinstance(scrape_dt, datetime.datetime)
    assert scrape_dt >= start_time


def test_detect_no_events_warning(parser, sps):  # Global Helper
    for sp in sps:
        no_events_warning = parser.detect_no_events_warning(sp)
        assert isinstance(no_events_warning, bool)


def test_detect_game_titles(parser, sps):  # Specific Helper
    for sp in sps:
        has_game_titles = parser._detect_game_titles(sp)
        assert isinstance(has_game_titles, bool)


def test_detect_event_headings(parser, sps):  # Specific Helper
    for sp in sps:
        has_event_headings = parser._detect_event_headings(sp)
        assert isinstance(has_event_headings, bool)


def test_detect_bet_type(parser, sps):  # Top Level
    bet_type_options = ['Game_Props', 'Game_Lines', 'Futures']
    for sp in sps:
        bet_type = parser.detect_bet_type(sp)
        assert isinstance(bet_type, str)
        assert bet_type in bet_type_options


def test_game_lines_df(parser):  # Specific Helper
    cols = ['Title', 'datetime', 'Game_Time', 'Home', 'Away',
            'Over_ESB', 'Over_ml_ESB', 'Under_ESB', 'Under_ml_ESB',
            'Home_Line_ESB', 'Home_Line_ml_ESB', 'Away_Line_ESB', 'Away_Line_ml_ESB',
            'Home_ML_ESB', 'Away_ML_ESB',
            'scraped_ts']

    df = parser._game_lines_df()
    assert isinstance(df, pd.DataFrame)
    assert list(df.columns) == cols
    assert len(df) == 0


def test_get_date_events(parser, game_lines_sps):  # Specific Helper
    for sp in game_lines_sps:
        date_events = parser._get_date_events(sp)
        assert isinstance(date_events, list)
        for item in date_events:
            assert isinstance(item, bs4.element.Tag)


def test_check_is_date(parser, game_lines_sps):  # Specific Helper
    for sp in game_lines_sps:
        date_events = parser._get_date_events(sp)
        date = None
        for date_event in date_events:
            date, found_date = parser._check_is_date(date_event, date)
            assert date is not None
            assert isinstance(date, datetime.datetime)


def test_game_time(parser, game_lines_events):  # Helping Helper
    game_time_comp = re.compile(r"^\d{2}:\d{2} C(D|S)T$")

    for event in game_lines_events:
        game_time = parser._game_time(event)
        assert isinstance(game_time, str)

        match = re.search(game_time_comp, game_time)
        assert match is not None


def test_teams(parser, game_lines_events):  # Helping Helper
    for event in game_lines_events:
        home, away, tie = parser._teams(event)

        assert isinstance(home, str)
        assert isinstance(away, str)
        if tie is not None:
            assert isinstance(tie, str)


def test_moneylines(parser, game_lines_events):  # Helping Helper
    for event in game_lines_events:
        home_ml, away_ml = parser._moneylines(event)

        assert ((isinstance(home_ml, float)) or (home_ml is None))
        assert ((isinstance(away_ml, float)) or (away_ml is None))


def test_spreads(parser, game_lines_events):  # Helping Helper
    for event in game_lines_events:
        home_spread, home_spread_ml, away_spread, away_spread_ml = parser._spreads(event)

        assert ((isinstance(home_spread, float)) or (home_spread is None))
        assert ((isinstance(home_spread_ml, float)) or (home_spread_ml is None))
        assert ((isinstance(away_spread, float)) or (away_spread is None))
        assert ((isinstance(away_spread_ml, float)) or (away_spread_ml is None))

        if home_spread is not None:
            assert home_spread_ml is not None
            assert away_spread is not None

        if away_spread is not None:
            assert away_spread_ml is not None
            assert home_spread is not None

        if home_spread_ml is not None:
            assert ((home_spread_ml >= 100) or (home_spread_ml <= -100))

        if away_spread_ml is not None:
            assert ((away_spread_ml >= 100) or (away_spread_ml <= -100))


def test_totals(parser, game_lines_events):  # Helping Helper
    for event in game_lines_events:
        over, over_ml, under, under_ml = parser._totals(event)

        assert ((isinstance(over, float)) or (over is None))
        assert ((isinstance(over_ml, float)) or (over_ml is None))
        assert ((isinstance(under, float)) or (under is None))
        assert ((isinstance(under_ml, float)) or (under_ml is None))

        if over is not None:
            assert over_ml is not None
            assert under is not None

        if under is not None:
            assert under_ml is not None
            assert over is not None

        if over_ml is not None:
            assert ((over_ml >= 100) or (over_ml <= -100))

        if under_ml is not None:
            assert ((under_ml >= 100) or (under_ml <= -100))


def test_date_event_to_row(parser, game_lines_events):  # Specific Helper
    dummy_date = datetime.date.today()
    for event in game_lines_events:
        row = parser._date_event_to_row(event, dummy_date)
        assert isinstance(row, list)

        assert row[0] == 'Full Game'
        assert isinstance(row[1], datetime.date)
        assert row[2] == parser._game_time(event)
        home, away, _ = parser._teams(event)
        assert row[3] == home
        assert row[4] == away
        over, over_ml, under, under_ml = parser._totals(event)
        assert row[5] == over
        assert row[6] == over_ml
        assert row[7] == under
        assert row[8] == under_ml
        home_spread, home_spread_ml, away_spread, away_spread_ml = parser._spreads(event)
        assert row[9] == home_spread
        assert row[10] == home_spread_ml
        assert row[11] == away_spread
        assert row[12] == away_spread_ml
        home_ml, away_ml = parser._moneylines(event)
        assert row[13] == home_ml
        assert row[14] == away_ml
        assert isinstance(row[15], str)
        scrape_dt = datetime.datetime.strptime(row[15], "%Y-%m-%d %H:%M")
        assert isinstance(scrape_dt, datetime.datetime)


def test_scrape_game_lines(parser, game_lines_sps):  # Top Level
    for sp in game_lines_sps:
        df = parser.scrape_game_lines(sp)
        assert isinstance(df, pd.DataFrame)


def test_game_props_df(parser):  # Specific Helper
    df = parser._game_props_df()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 0

    cols = ['datetime', 'Game_Time', 'Home', 'Away', 'Title', 'Description', 'Bet',
            'Spread/overunder', 'Odds', 'scraped_ts']
    assert list(df.columns) == cols


def test_find_page_title(parser, game_props_sps):  # Specific Helper
    for sp in game_props_sps:
        title = parser._page_title(sp)
        assert isinstance(title, str)


def test_description(parser, game_props_events):  # Specific Helper
    for event in game_props_events:
        description = parser._description(event)
        assert isinstance(description, str)
