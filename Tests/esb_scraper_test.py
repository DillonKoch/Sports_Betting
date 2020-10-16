# ==============================================================================
# File: esb_scraper_test.py
# Project: Tests
# File Created: Thursday, 15th October 2020 7:30:42 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 15th October 2020 7:36:53 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Test suite for esb_scraper.py
# ==============================================================================

import sys
from os.path import abspath, dirname

import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from ESB.esb_scraper import ESB_Scraper


@pytest.fixture  # Fixture
def scraper():
    return ESB_Scraper()


def test_setup(scraper):
    assert scraper.start_link == 'https://www.elitesportsbook.com/sports/home.sbk'
