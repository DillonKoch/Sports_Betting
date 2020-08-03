# ==============================================================================
# File: espn_game_test.py
# Project: Tests
# File Created: Tuesday, 30th June 2020 4:38:04 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 2nd August 2020 1:49:00 pm
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
    """
    Test class for the ESPN Game object
    """

    def setUp(self):
        pass

    def test_get_ncaab_scores(self):
        g = Game("NCAAB")
        g.final_status = "Final"
        g.home_half_scores = ["32", "48", None]
        g.away_half_scores = ["45", "34", None]

        scores = g._get_ncaab_scores()
        self.assertEqual(["32", "48", None, "45", "34", None], scores)

    def test_get_ncaab_scores_OT(self):
        g = Game("NCAAB")
        g.final_status = "Final/OT"
        g.home_half_scores = ["32", "48", "23"]
        g.away_half_scores = ["48", "32", "12"]

        scores = g._get_ncaab_scores()
        self.assertEqual(["32", "48", "23", "48", "32", "12"], scores)

    def test_get_ncaab_scores_in_progress(self):
        g = Game("NCAAB")
        g.final_status = "10:32 1H"
        g.home_half_scores = [None, None, None]
        g.away_half_scores = [None, None, None]
        self.assertEqual([None] * 6, g._get_ncaab_scores())

    def test_get_non_ncaab_scores(self):
        for league in ["NFL", "NCAAF", "NBA"]:
            g = Game(league)
            g.final_status = "Final"
            g.home_qscores = ["7", "14", "0", "10", None]
            g.away_qscores = ["3", "6", "14", "7", None]

            scores = g._get_non_ncaab_scores()
            self.assertEqual(["7", "14", "0", "10", None, "3", "6", "14", "7", None], scores)

    def test_get_non_ncaab_scores_OT(self):
        for league in ["NFL", "NCAAF", "NBA"]:
            g = Game(league)
            g.final_status = "Final/OT"
            g.home_qscores = ["7", "14", "0", "10", "7"]
            g.away_qscores = ["3", "6", "14", "7", "3"]

            scores = g._get_non_ncaab_scores()
            self.assertEqual(["7", "14", "0", "10", "7", "3", "6", "14", "7", "3"], scores)

    def test_to_row_list_ncaab(self):
        g = Game("NCAAB")
        g.ESPN_ID = '400915001'  # this is a real game, not all real stats
        season = "2016"
        g.game_date = "December 17, 2016"
        g.home_name = "Iowa Hawkeyes"
        g.away_name = "Northern Iowa Panthers"
        g.home_record = "6-5"
        g.away_record = "5-5"
        g.home_score = "69"
        g.away_score = "46"
        g.line = "Iowa -10"
        g.over_under = "124"
        g.final_status = "Final"
        g.network = "ESPN"
        g.home_half_scores = ["34", "35", None]
        g.away_half_scores = ["16", "30", None]

        lis = [g.ESPN_ID, season, g.game_date, g.home_name, g.away_name,
               g.home_record, g.away_record, g.home_score, g.away_score, g.line,
               g.over_under, g.final_status, g.network, *g.home_half_scores,
               *g.away_half_scores, "NCAAB"]

        game_lis = g.to_row_list("NCAAB", "2016")
        self.assertEqual(lis, game_lis)

    def test_to_row_list_nfl(self):
        g = Game("NFL")
        g.ESPN_ID = "401030777"
        season = "2018"
        g.game_date = "September 23, 2018"
        g.home_name = "Atlanta Falcons"
        g.away_name = "New Orleans Saints"
        g.home_record = "1-2"
        g.away_record = "2-1"
        g.home_score = "37"
        g.away_score = "43"
        g.line = "ATL -2.0"
        g.over_under = "54"
        g.final_status = "Final/OT"
        g.network = "FOX"
        g.home_qscores = ['7', '7', '7', '16', '0']
        g.away_qscores = ['7', '9', '7', '14', '6']

        lis = [g.ESPN_ID, season, g.game_date, g.home_name, g.away_name,
               g.home_record, g.away_record, g.home_score, g.away_score, g.line,
               g.over_under, g.final_status, g.network, *g.home_qscores,
               *g.away_qscores, "3", "NFL"]

        game_lis = g.to_row_list("NFL", "2018", "3")
        self.assertEqual(lis, game_lis)

    def test_to_row_list_ncaaf_nba(self):
        g = Game("NBA")
        g.ESPN_ID = "401224714"
        season = "2019"
        g.game_date = "August 1, 2020"
        g.home_name = "Denver Nuggets"
        g.away_name = "Miami Heat"
        g.home_record = "43-23"
        g.away_record = "42-24"
        g.home_score = "105"
        g.away_score = "125"
        g.line = "MIA - 4.0"
        g.over_under = "228"
        g.final_status = "Final"
        g.network = "ESPN"
        g.home_qscores = ['26', '31', '22', '26', None]
        g.away_qscores = ['28', '28', '38', '31', None]

        lis = [g.ESPN_ID, season, g.game_date, g.home_name, g.away_name,
               g.home_record, g.away_record, g.home_score, g.away_score, g.line,
               g.over_under, g.final_status, g.network, *g.home_qscores,
               *g.away_qscores, "NBA"]

        game_lis = g.to_row_list("NBA", "2019")
        self.assertEqual(lis, game_lis)
