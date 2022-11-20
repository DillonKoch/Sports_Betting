# ==============================================================================
# File: esb_parser_test.py
# Project: test
# File Created: Sunday, 16th May 2021 9:20:07 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 16th May 2021 9:20:07 pm
# Modified By: Dillon Koch
# -----
#
# -----
# test suite for esb_parser.py
# ==============================================================================


import os
import pickle
import sys
from os.path import abspath, dirname

import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from scrapers.esb_parser import ESB_Parser


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


@pytest.fixture  # Fixture
def esb_parser():
    return ESB_Parser()


@pytest.fixture  # Fixture
def league_htmls():
    folder = ROOT_PATH + "/test/data/esb/"
    files = listdir_fullpath(folder)

    league_htmls = []
    for file in files:
        league = file.split('/')[-1].split('_')[0]
        with open(file, 'rb') as f:
            html = pickle.load(f)
        league_htmls.append((league, html))
    return league_htmls


def test_nothing(esb_parser, league_htmls):
    for league_html in league_htmls:
        league, html = league_html
        print(league)
