# ==============================================================================
# File: esb_parser_test.py
# Project: Tests
# File Created: Saturday, 17th October 2020 9:19:51 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 17th October 2020 9:32:06 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Test suite for esb_parser.py
# ==============================================================================


import datetime
import sys
from os.path import abspath, dirname

import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from ESB.esb_parser import ESB_Parser


@pytest.fixture  # Fixture
def leagues():
    return ['NFL', 'NBA', 'NCAAF', 'NCAAB']


@pytest.fixture  # Fixture
def parsers(leagues):
    parsers = []
    for league in leagues:
        parser = ESB_Parser(league)
        parsers.append(parser)
    return parsers


def test_get_scrape_ts(parsers):  # Global Helper
    start_time = datetime.datetime.now().replace(second=0, microsecond=0)
    for parser in parsers:
        scrape_ts = parser._get_scrape_ts()
        assert isinstance(scrape_ts, str)

        scrape_dt = datetime.datetime.strptime(scrape_ts, "%Y-%m-%d %H:%M")
        assert isinstance(scrape_dt, datetime.datetime)
        assert scrape_dt >= start_time
