# ==============================================================================
# File: ncaaf_season_scraper_test.py
# Project: Season_Scrapers
# File Created: Monday, 4th May 2020 4:19:19 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 9th May 2020 5:15:49 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Testing NCAAF Season scraper, which inherits from espn_season_scraper.py
# ==============================================================================

from unittest import TestCase

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Season_Scrapers.ncaaf_season_scraper import NCAAF_Season_Scraper


class Test_NCAAF_Season_Scraper(TestCase):
    def setUp(self):
        pass

    def test_something(self):
        pass
