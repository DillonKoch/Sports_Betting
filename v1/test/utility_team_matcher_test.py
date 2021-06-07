# ==============================================================================
# File: utility_team_matcher_test.py
# Project: Tests
# File Created: Sunday, 25th October 2020 7:26:39 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 25th October 2020 7:27:40 pm
# Modified By: Dillon Koch
# -----
#
# -----
# test suite for team_matcher.py
# ==============================================================================


import sys
from os.path import abspath, dirname

import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Utility.team_matcher import Team_Matcher


@pytest.fixture
def team_matcher():
    return Team_Matcher()


def test_nothing():
    assert True
