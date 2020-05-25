# ==============================================================================
# File: espn_season_scraper_test.py
# Project: Season_Scrapers
# File Created: Tuesday, 14th April 2020 5:08:35 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 25th May 2020 3:18:26 pm
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
    nba = ESPN_Season_Scraper("NBA")
    nfl = ESPN_Season_Scraper("NFL")
    ncaaf = ESPN_Season_Scraper("NCAAF")
    ncaab = ESPN_Season_Scraper("NCAAB")
    all_scrapers = [nba, nfl, ncaaf, ncaab]

    nba_sections = nba._get_game_sections('mia', '2019')
    nba_links = []
    nba_dates = []
    for section in nba_sections:
        link, date = nba._link_week_from_game_section(section)
        nba_links.append(link)
        nba_dates.append(date)

    nfl_sections = nfl._get_game_sections('min', '2019')
    nfl_links = []
    nfl_weeks = []
    for section in nfl_sections:
        link, week = nfl._link_week_from_game_section(section)
        nfl_links.append(link)
        nfl_weeks.append(week)
        print(link)
        print(week)

    def setUp(self):
        pass

    def test_setup(self):
        true_keys = ["Teams", "Season Base Link", "DF Columns"]
        for scraper in self.all_scrapers:
            config = scraper.config
            self.assertIsInstance(config, dict)
            keys = list(config.keys())
            self.assertEqual(true_keys, keys)

    def test_get_game_sections_nba(self):
        self.assertEqual(83, len(self.nba_sections))

    def test_link_week_from_game_section_nba(self):
        none_count = 0
        link_count = 0
        for link in self.nba_links:
            if isinstance(link, str):
                link_count += 1
            elif link is None:
                none_count += 1
        self.assertEqual(1, none_count)
        self.assertEqual(82, link_count)

        links = [item for item in self.nba_links if item is not None]
        for link in links:
            self.assertTrue('http://www.espn.com/nba/game?gameId=' in link)
            for item in link[-9:]:
                self.assertTrue(item in "0123456789")

    def test_link_week_to_row_nba(self):
        df = self.nba._make_season_df()
        links = [item for item in self.nba_links if isinstance(item, str)]
        dates = [date for date in self.nba_dates if isinstance(date, str)]
        for link, date in zip(links[:3], dates[:3]):
            df = self.nba._link_week_to_row(df, link, date, '2019')

        self.assertEqual(3, df.shape[0])

    def test_get_game_sections_ncaaf(self):
        pass
