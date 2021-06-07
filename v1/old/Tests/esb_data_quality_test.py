# ==============================================================================
# File: esb_data_quality_test.py
# Project: Tests
# File Created: Friday, 28th August 2020 3:04:53 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 28th August 2020 3:07:36 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Testing data quality of all saved csv's in ESB module
# ==============================================================================


from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from unittest import TestCase


class Test_ESB_Data(TestCase):

    def setUp(self):
        # bool prop
        # prop
        # game
        # multiple futures

        pass
