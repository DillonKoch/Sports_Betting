# ==============================================================================
# File: test_sbo_odds.py
# Project: Tests
# File Created: Sunday, 6th June 2021 8:41:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 6th June 2021 8:42:00 pm
# Modified By: Dillon Koch
# -----
#
# -----
# test suite for sbo_odds.py
# ==============================================================================

import pytest

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Scrapers.sbo_odds import Sbo_Odds


@pytest.fixture  # Fixture
def Sbo_Odds():
    return Sbo_Odds()
