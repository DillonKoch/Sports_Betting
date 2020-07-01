# ==============================================================================
# File: espn_game_scraper_test2.py
# Project: Tests
# File Created: Wednesday, 1st July 2020 9:23:53 am
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 1st July 2020 9:56:26 am
# Modified By: Dillon Koch
# -----
#
# -----
# Tests for the ESPN Game Scraper
# ==============================================================================

import sys
from os.path import abspath, dirname
from unittest import TestCase


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN_Scrapers.espn_game_scraper import ESPN_Game_Scraper


class Test_ESPN_Game_Scraper(TestCase):

    nfl = ESPN_Game_Scraper("NFL")
    nba = ESPN_Game_Scraper("NBA")
    ncaaf = ESPN_Game_Scraper("NCAAF")
    ncaab = ESPN_Game_Scraper("NCAAB")

    nfl_game_id = "401128044"
    nfl_sp = nfl._sp_helper(nfl_game_id)
    nba_game_id = "401160782"
    nba_sp = nba._sp_helper(nba_game_id)
    ncaaf_game_id = "401112199"
    ncaaf_sp = ncaaf._sp_helper(ncaaf_game_id)
    ncaab_game_id = "401166198"
    ncaab_sp = ncaab._sp_helper(ncaab_game_id)

    def setUp(self):
        pass

    def test_nfl_team_names(self):
        home_name, away_name = self.nfl.team_names(self.nfl_game_id, sp=self.nfl_sp)
        self.assertEqual("Cleveland Browns", home_name)
        self.assertEqual("Pittsburgh Steelers", away_name)

        home_name, away_name = self.nfl.team_names("4011asnvisd")
        self.assertEqual(None, home_name)
        self.assertEqual(None, away_name)

    def test_nfl_records(self):
        home_record, away_record = self.nfl.team_records(self.nfl_game_id, sp=self.nfl_sp)
        self.assertEqual("4-6, 2-3 Home", home_record)
        self.assertEqual("5-5, 1-3 Away", away_record)

        home_record, away_record = self.nfl.team_records("40119999999")
        self.assertEqual(None, home_record)
        self.assertEqual(None, away_record)

    def test_nfl_final_status(self):
        status = self.nfl.final_status(self.nfl_game_id, sp=self.nfl_sp)
        self.assertEqual("Final", status)

        status = self.nfl.final_status("40112983789")
        self.assertEqual(None, status)

    def test_nfl_quarter_scores(self):
        home_scores, away_scores = self.nfl.quarter_scores(self.nfl_game_id, sp=self.nfl_sp)
        self.assertEqual(['7', '7', '0', '7', None], home_scores)
        self.assertEqual(['0', '0', '7', '0', None], away_scores)

        home_scores, away_scores = self.nfl.quarter_scores("09a789798326")
        none_result = [None] * 5
        self.assertEqual(none_result, home_scores)
        self.assertEqual(none_result, away_scores)

    def test_nfl_overtime_quarter_scores(self):
        home_scores, away_scores = self.nfl.quarter_scores("401127972")
        self.assertEqual(['7', '10', '7', '0', '6'], home_scores)
        self.assertEqual(['0', '6', '10', '8', '0'], away_scores)

        home_scores, away_scores = self.nfl.quarter_scores("asdvndk")
        none_result = [None] * 5
        self.assertEqual(none_result, home_scores)
        self.assertEqual(none_result, away_scores)

    def test_nfl_scores(self):
        home_score, away_score = self.nfl._game_scores("NFL", self.nfl_game_id, sp=self.nfl_sp)
        self.assertEqual("21", home_score)
        self.assertEqual("7", away_score)

        home_score, away_score = self.nfl._game_scores("NFL", "4011579")
        self.assertEqual(None, home_score)
        self.assertEqual(None, away_score)

    # def test_nfl_game_network(self):
    #     network = self.nfl._game_network("NFL", self.nfl_game_id, sp=self.nfl_sp)
    #     self.assertEqual("FOX/NFL", network)

    #     network = self.nfl._game_network("NFL", "401283229")
    #     self.assertEqual(None, network)

    # def test_nfl_line_ou(self):
    #     line, over_under = self.nfl._line_ou("NFL", self.nfl_game_id, sp=self.nfl_sp)
    #     self.assertEqual("CLE -3.0", line)
    #     self.assertEqual("42", over_under)

    #     line, over_under = self.nfl._line_ou("NFL", "298374930")
    #     self.assertEqual(None, line)
    #     self.assertEqual(None, over_under)

    # def test_nfl_game_date(self):
    #     game_date = self.nfl._game_date("NFL", self.nfl_game_id, sp=self.nfl_sp)
    #     self.assertEqual('November 14, 2019', game_date)

    # def test_all_nfl_info(self):
    #     game = self.nfl.all_nfl_info(self.nfl_game_id, sp=self.nfl_sp)
    #     self.assertEqual(self.nfl_game_id, game.ESPN_ID)
    #     self.assertEqual("Cleveland Browns", game.home_name)
    #     self.assertEqual("Pittsburgh Steelers", game.away_name)
    #     self.assertEqual("4-6, 2-3 Home", game.home_record)
    #     self.assertEqual("5-5, 1-3 Away", game.away_record)
    #     self.assertEqual("Final", game.final_status)
    #     self.assertEqual(['7', '7', '0', '7'], game.home_qscores)
    #     self.assertEqual(['0', '0', '7', '0'], game.away_qscores)
    #     self.assertEqual("21", game.home_score)
    #     self.assertEqual("7", game.away_score)
    #     self.assertEqual("FOX/NFL", game.network)
    #     self.assertEqual("CLE -3.0", game.line)
    #     self.assertEqual("42", game.over_under)
    #     self.assertEqual("November 14, 2019", game.game_date)
