# ==============================================================================
# File: espn_game_test.py
# Project: Tests
# File Created: Tuesday, 30th June 2020 4:38:04 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 1st July 2020 10:47:34 am
# Modified By: Dillon Koch
# -----
#
# -----
# Test file for the ESPN Game object
# ==============================================================================


from os.path import abspath, dirname
from unittest import TestCase
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from ESPN_Scrapers.espn_game import Game


class Test_ESPN_Game(TestCase):
    nfl_game_id = "401128044"
    nba_game_id = "401160782"
    ncaaf_game_id = "401112199"
    ncaab_game_id = "401166198"

    def setUp(self):
        pass

    def test_get_ncaab_scores(self):
        g = Game("NCAAB")
        g.home_half_scores = ["32", "48", None]
        g.away_half_scores = ["45", "34", None]

        scores = g._get_ncaab_scores()
        self.assertEqual(["32", "48", None, "45", "34", None], scores)

    def test_get_ncaab_scores_OT(self):
        g = Game("NCAAB")
        g.home_half_scores = ["32", "48", "23"]
        g.away_half_scores = ["48", "32", "12"]

        scores = g._get_ncaab_scores()
        self.assertEqual(["32", "48", "23", "48", "32", "12"], scores)

    def test_get_ncaab_scores_fuzz(self):
        g = Game("NCAAB")
        g.home_half_scores = [None, None, None]
        g.away_half_scores = [None, None, None]
        self.assertEqual([None] * 6, g._get_ncaab_scores())

    def test_get_non_ncaab_scores(self):
        for league in ["NFL", "NCAAF", "NBA"]:
            g = Game(league)
            g.home_qscores = ["7", "14", "0", "10", None]
            g.away_qscores = ["3", "6", "14", "7", None]

            scores = g._get_non_ncaab_scores()
            self.assertEqual(["7", "14", "0", "10", None, "3", "6", "14", "7", None], scores)

    def test_get_non_ncaab_scores_OT(self):
        for league in ["NFL", "NCAAF", "NBA"]:
            g = Game(league)
            g.home_qscores = ["7", "14", "0", "10", "7"]
            g.away_qscores = ["3", "6", "14", "7", "3"]

            scores = g._get_non_ncaab_scores()
            self.assertEqual(["7", "14", "0", "10", "7", "3", "6", "14", "7", "3"], scores)
