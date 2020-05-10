# ==============================================================================
# File: espn_season_scraper_test.py
# Project: Season_Scrapers
# File Created: Tuesday, 14th April 2020 5:08:35 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 9th May 2020 7:03:35 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Testing main ESPN season scraper
# ==============================================================================

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Season_Scrapers.espn_season_scraper import ESPN_Season_Scraper
# from Season_Scrapers.espn_game_scraper import ESPN_Game_Scraper

from unittest import TestCase


class Test_ESPN_Season_Scraper(TestCase):
    def setUp(self):
        self.ess = ESPN_Season_Scraper()
        self.ess.league = "NBA"

    def test_setup(self):
        self.assertIsInstance(self.ess.json_data, dict)
        keys = ['Teams', 'Season Base Link', "DF Columns"]
        self.assertEqual(keys, list(self.ess.json_data.keys()))
