# ==============================================================================
# File: nfl_season_scraper_test.py
# Project: Season_Scrapers
# File Created: Saturday, 2nd May 2020 7:47:01 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 2nd May 2020 7:56:20 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Testing NFL Season Scraper
# ==============================================================================

from unittest import TestCase

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Season_Scrapers.nfl_season_scraper import NFL_Season_Scraper


class Test_NFL_Season_Scraper(TestCase):

    scraper = NFL_Season_Scraper()
    sections = scraper._get_game_sections('min', '2019')

    def setUp(self):
        pass

    def test_sections(self):
        self.assertEqual(28, len(self.sections))
