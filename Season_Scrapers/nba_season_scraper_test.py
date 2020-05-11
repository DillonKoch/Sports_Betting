# ==============================================================================
# File: nba_season_scraper_test.py
# Project: Season_Scrapers
# File Created: Saturday, 2nd May 2020 7:29:14 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 10th May 2020 3:33:17 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Testing nba_season_scraper.py
# ==============================================================================

import sys
from os.path import abspath, dirname
from unittest import TestCase

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Season_Scrapers.nba_season_scraper import NBA_Season_Scraper


class Test_NBA_Season_Scraper(TestCase):

    scraper = NBA_Season_Scraper()
    sections = scraper._get_game_sections('mia', '2013')

    def setUp(self):
        pass

    def test_json_data(self):
        self.assertIsInstance(self.scraper.json_data, dict)
        self.assertEqual(['Teams', 'Season Base Link', 'DF Columns'], list(self.scraper.json_data.keys()))

    def test_get_game_sections(self):
        self.assertEqual(83, len(self.sections))
        for section in self.sections:
            self.assertTrue('bs4.element.Tag' in str(type(section)))

    def test_link_gameid_from_section(self):
        link_null_count = 0
        link_str_count = 0
        gameid_null_count = 0
        gameid_str_count = 0
        for section in self.sections:
            link, gameid = self.scraper._link_gameid_from_section(section)
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

        self.assertEqual(82, link_str_count)
        self.assertEqual(1, link_null_count)
        self.assertEqual(82, gameid_str_count)
        self.assertEqual(1, gameid_null_count)

    def test_team_gameid_links(self):
        games = self.scraper.team_gameid_links('mia', '2019')
        self.assertIsInstance(games, list)
        for item in games:
            self.assertIsInstance(item, tuple)
            for subitem in item:
                self.assertIsInstance(subitem, str)
        self.assertEqual(82, len(games))

    def test_make_season_df(self):
        df = self.scraper._make_season_df()
        self.assertIsInstance(df, pd.DataFrame)
        df_cols = list(df.columns)
        self.assertEqual(self.scraper.json_data["DF Columns"], df_cols)
