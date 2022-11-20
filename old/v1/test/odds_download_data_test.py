# ==============================================================================
# File: odds_download_data_test.py
# Project: Tests
# File Created: Sunday, 25th October 2020 10:43:46 am
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 25th October 2020 1:13:26 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Test suite for Odds/download_data.py
# ==============================================================================

import datetime
import os
import re
import sys
from os.path import abspath, dirname

import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Odds.download_data import Download_Data


@pytest.fixture  # Fixture
def download_data():
    return Download_Data()


@pytest.fixture  # Fixture
def leagues():
    return ['NFL', 'NBA', 'NCAAF', 'NCAAB']


def test_get_year_strs(download_data):  # Global Helper
    current_year_str, last_year_str = download_data._get_year_strs()
    year_str_comp = re.compile(r"^\d{4}-\d{2}$")
    for year_str in [current_year_str, last_year_str]:
        match = re.match(year_str_comp, year_str)
        assert match is not None

        full_year = int(year_str[:4])
        current_year = datetime.date.today().year
        assert abs(current_year - full_year) <= 1


def test_get_ncaa_urls(download_data):  # Top Level
    ncaa_comp = re.compile(
        r"^https://www.sportsbookreviewsonline.com/scoresoddsarchives/ncaa(football|basketball)/ncaa (football|basketball) \d{4}-\d{2}.xlsx$")
    for league in ['NCAAF', 'NCAAB']:
        urls = download_data.get_ncaa_urls(league)
        for url in urls:
            assert isinstance(url, str)
            assert league.lower() in url
            match = re.match(ncaa_comp, url)
            assert match is not None


def test_get_pro_urls(download_data):  # Top Level
    pro_comp = re.compile(
        r"^https://www.sportsbookreviewsonline.com/scoresoddsarchives/(nfl|nba)/(nfl|nba) odds \d{4}-\d{2}.xlsx$")
    for league in ['NFL', 'NBA']:
        urls = download_data.get_pro_urls(league)
        for url in urls:
            assert isinstance(url, str)
            assert league.lower() in url
            match = re.match(pro_comp, url)
            assert match is not None


def test_remove_old_file(download_data, leagues):  # Top Level
    for league in leagues:
        urls = download_data.get_ncaa_urls(league) if 'NCAA' in league else download_data.get_pro_urls(league)
        for url in urls:
            file = url.split('/')[-1]
            filepath = ROOT_PATH + f"/Odds/{league}/{file}"

            if os.path.isfile(filepath):
                download_data.remove_old_file(url, league)
                assert not os.path.isfile(filepath)
                download_data.download_file(url, league)


def test_download_file(download_data, leagues):  # Top Level
    for league in leagues:
        urls = download_data.get_ncaa_urls(league) if 'NCAA' in league else download_data.get_pro_urls(league)
        for url in urls:
            download_data.remove_old_file(url, league)
            download_data.download_file(url, league)
