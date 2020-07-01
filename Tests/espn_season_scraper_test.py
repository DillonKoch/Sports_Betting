# ==============================================================================
# File: espn_season_scraper_test.py
# Project: Season_Scrapers
# File Created: Tuesday, 14th April 2020 5:08:35 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 1st July 2020 11:19:50 am
# Modified By: Dillon Koch
# -----
#
# -----
# Testing main ESPN season scraper
# ==============================================================================

import re
import sys
from os.path import abspath, dirname
from unittest import TestCase

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN_Scrapers.espn_season_scraper import ESPN_Season_Scraper


class Test_ESPN_Season_Scraper(TestCase):
    nba = ESPN_Season_Scraper("NBA")
    nfl = ESPN_Season_Scraper("NFL")
    ncaaf = ESPN_Season_Scraper("NCAAF")
    ncaab = ESPN_Season_Scraper("NCAAB")
    all_scrapers = [nba, nfl, ncaaf, ncaab]

    nba_sections = nba._get_game_sections('mia', '2019')
    # nba_links = []
    # nba_dates = []
    # for section in nba_sections:
    #     link, date = nba._link_week_from_game_section(section)
    #     nba_links.append(link)
    #     nba_dates.append(date)

    nfl_sections = nfl._get_game_sections('min', '2019')
    # nfl_links = []
    # nfl_weeks = []
    # for section in nfl_sections:
    #     link, week = nfl._link_week_from_game_section(section)
    #     nfl_links.append(link)
    #     nfl_weeks.append(week)

    ncaaf_sections = ncaaf._get_game_sections('2294', '2019')
    # ncaaf_links = []
    # ncaaf_weeks = []
    # for section in ncaaf_sections:
    #     link, week = ncaaf._link_week_from_game_section(section)
    #     ncaaf_links.append(link)
    #     ncaaf_weeks.append(date)

    ncaab_sections = ncaab._get_game_sections('2294', '2019')

    all_sections = [nfl_sections, nba_sections, ncaaf_sections, ncaab_sections]

    ###########################################################################

    def setUp(self):
        pass

    def test_setup(self):
        true_keys = ["DF Columns", "Season Base Link", "Teams"]
        for scraper in self.all_scrapers:
            config = scraper.config
            self.assertIsInstance(config, dict)
            keys = list(config.keys())
            self.assertEqual(true_keys, keys)

            self.assertIsInstance(scraper.game_link_re, re.Pattern)

    def test_q_amount(self):
        self.assertEqual(self.nfl.q_amount, 4)
        self.assertEqual(self.nba.q_amount, 4)
        self.assertEqual(self.ncaaf.q_amount, 4)
        self.assertEqual(self.ncaab.q_amount, 2)

    def test_make_season_df(self):
        for scraper in self.all_scrapers:
            df = scraper._make_season_df()
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(scraper.config["DF Columns"], list(df.columns))

    def test_get_game_sections(self):
        for sections_list in self.all_sections:
            for section in sections_list:
                self.assertEqual("<class 'bs4.element.Tag'>", str(type(section)))

    def test_week_from_section(self):
        weeks = [self.nfl._week_from_section(section) for section in self.nfl_sections]

        nfl_weeks = [str(item) for item in range(1, 18, 1)]
        week_count = 0
        for item in weeks:
            if item in nfl_weeks:
                week_count += 1
        self.assertEqual(21, week_count)

    def test_link_from_game_section(self):
        nfl_links = [self.nfl._link_from_game_section(section) for section in self.nfl_sections]
        nfl_links = [item for item in nfl_links if item is not None]
        self.assertEqual(22, len(nfl_links))

        nba_links = [self.nba._link_from_game_section(section) for section in self.nba_sections]
        nba_links = [item for item in nba_links if item is not None]
        self.assertEqual(82, len(nba_links))

        ncaaf_links = [self.ncaaf._link_from_game_section(section) for section in self.ncaaf_sections]
        ncaaf_links = [item for item in ncaaf_links if item is not None]
        self.assertEqual(13, len(ncaaf_links))

        ncaab_links = [self.ncaab._link_from_game_section(section) for section in self.ncaab_sections]
        ncaab_links = [item for item in ncaab_links if item is not None]
        self.assertEqual(35, len(ncaab_links))

        all_links = nfl_links + nba_links + ncaaf_links + ncaab_links
        for link in all_links:
            self.assertIsInstance(link, str)
