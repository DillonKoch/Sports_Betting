# ==============================================================================
# File: ncaaf_season_scraper_test.py
# Project: Season_Scrapers
# File Created: Monday, 4th May 2020 4:19:19 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 9th May 2020 9:23:33 pm
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

    scraper = NCAAF_Season_Scraper()
    sections = scraper._get_game_sections('228', '2019')

    def setUp(self):
        pass

    def test_json_data(self):
        self.assertIsInstance(self.scraper.json_data, dict)
        self.assertEqual(['Teams', 'Season Base Link', 'DF Columns'], list(self.scraper.json_data.keys()))

    def test_get_game_sections(self):
        self.assertEqual(20, len(self.sections))
        for section in self.sections:
            self.assertTrue('bs4.element.Tag' in str(type(section)))

    def test_link_gameid_from_section(self):
        link_null_count = 0
        link_str_count = 0
        gameid_null_count = 0
        gameid_str_count = 0
        for section in self.sections:
            link, gameid = self.scraper._link_gameid_from_section("NCAAF", section)
            self.assertIsInstance(link, str)
            self.assertIsInstance(gameid, str)

            if link == 'NULL':
                link_null_count += 1
            else:
                link_str_count += 1

            if gameid == 'NULL':
                gameid_null_count += 1
            else:
                gameid_str_count += 1

        self.assertEqual(15, link_str_count)
        self.assertEqual(5, link_null_count)
        self.assertEqual(15, gameid_str_count)
        self.assertEqual(5, gameid_null_count)
