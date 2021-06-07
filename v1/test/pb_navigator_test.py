# ==============================================================================
# File: pb_navigator_test.py
# Project: Tests
# File Created: Thursday, 31st December 2020 7:01:17 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 31st December 2020 7:01:37 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Test suite for pb_navigator.py
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


import pytest
