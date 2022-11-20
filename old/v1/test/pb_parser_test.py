# ==============================================================================
# File: pb_parser_test.py
# Project: Tests
# File Created: Friday, 1st January 2021 12:50:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 1st January 2021 12:51:40 pm
# Modified By: Dillon Koch
# -----
#
# -----
# test suite for pb_parser.py
# ==============================================================================


import sys
import pytest
from os.path import abspath, dirname

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from PB.pb_parser import PB_Parser


@pytest.fixture  # Fixture
def parser():
    return PB_Parser()


def test_nothing():
    pass
