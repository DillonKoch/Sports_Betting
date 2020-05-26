# ==============================================================================
# File: ncaab_season_scraper_test.py
# Project: Season_Scrapers
# File Created: Monday, 4th May 2020 4:19:07 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 9th May 2020 5:15:21 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Testing NCAAB season scraper, which inherits from espn_season_scraper
# ==============================================================================

from unittest import TestCase

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Season_Scrapers.ncaab_season_scraper import NCAAB_Season_Scraper


class Test_NCAAB_Season_Scraper(TestCase):
    def setUp(self):
        pass

    def test_something(Self):
        pass
