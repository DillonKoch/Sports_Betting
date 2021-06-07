# ==============================================================================
# File: esb_game_scraper_test.py
# Project: Tests
# File Created: Saturday, 22nd August 2020 7:48:31 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 22nd August 2020 8:44:52 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Test file for the Elite Sportsbook Game Lines scraper
# ==============================================================================


from os.path import abspath, dirname
import sys
import pickle
from bs4 import BeautifulSoup as soup
import bs4
import re

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESB.esb_game_scraper import ESB_Game_Scraper

from unittest import TestCase


class Test_ESB_Game_Scraper(TestCase):

    def setUp(self):
        self.nfl = ESB_Game_Scraper("NFL", "Game_Lines", self.get_nfl_sp())

    def get_nfl_sp(self):
        with open("nfl_game_lines_sp.pickle", "rb") as f:
            str_sp = pickle.load(f)
        sp = soup(str_sp, features="html.parser")
        return sp

    def test_df_cols(self):
        self.assertIsInstance(self.nfl.df_cols, list)

    def test_get_date_event_boxes(self):
        """
        getting box_date_pairs and asserting they are the correct type
        """
        box_date_pairs = self.nfl.get_date_event_boxes()
        self.assertEqual(16, len(box_date_pairs))

        for pair in box_date_pairs:
            box, date = pair
            self.assertIsInstance(box, bs4.element.Tag)
            self.assertIsInstance(date, str)

    def test_game_box_time(self):
        """
        getting box_date_pairs, ensuring time_str is str and matches regex expression for time
        """
        box_date_pairs = self.nfl.get_date_event_boxes()
        for pair in box_date_pairs:
            box, date = pair
            time_str = self.nfl._game_box_time(box)
            self.assertIsInstance(time_str, str)
            time_pattern = re.compile(r"^\d\d:\d\d CDT$")
            match = re.search(time_pattern, time_str)
            if match is None:
                assert ValueError("box time did not match regex expression: {}".format(time_str))

    def test_game_box_teams(self):
        """
        getting the teams in each box and asserting correct types
        """
        box_date_pairs = self.nfl.get_date_event_boxes()
        for pair in box_date_pairs:
            box, date = pair
            teams = self.nfl._game_box_teams(box)
            self.assertIsInstance(teams, list)
            self.assertEqual(2, len(teams))
