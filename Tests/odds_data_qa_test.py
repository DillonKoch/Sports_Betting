# ==============================================================================
# File: odds_data_qa_test.py
# Project: Tests
# File Created: Saturday, 24th October 2020 8:20:38 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 24th October 2020 8:22:24 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Quality assurance for data in the Odds module
# ==============================================================================


import sys
from os.path import abspath, dirname

import pytest

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)
