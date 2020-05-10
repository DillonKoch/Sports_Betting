# ==============================================================================
# File: nba_season_scraper_test.py
# Project: Season_Scrapers
# File Created: Saturday, 2nd May 2020 7:29:14 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 9th May 2020 7:10:43 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Testing nba_season_scraper.py
# ==============================================================================

from unittest import TestCase

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Season_Scrapers.nba_season_scraper import NBA_Season_Scraper


class Test_NBA_Season_Scraper(TestCase):

    scraper = NBA_Season_Scraper()
    sections = scraper._get_game_sections('mia', '2020')

    dates = []
    for section in sections:
        dates.append(scraper._game_date_from_section(section))

    def setUp(self):
        pass

    def test_json_data(self):
        self.assertIsInstance(self.scraper.json_data, dict)
        self.assertEqual(['Teams', 'Season Base Link', 'DF Columns'], list(self.scraper.json_data.keys()))

    def test_get_game_sections(self):
        self.assertEqual(83, len(self.sections))
        for section in self.sections:
            self.assertTrue('bs4.element.Tag' in str(type(section)))

    def test_section_dates(self):
        self.assertEqual(83, len(self.dates))
        self.assertIsInstance(self.dates, list)
        none_count = 0
        str_count = 0
        for item in self.dates:
            if isinstance(item, str):
                str_count += 1
            elif item is None:
                none_count += 1

        self.assertEqual(1, none_count)
        self.assertEqual(82, str_count)
