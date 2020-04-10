# ==============================================================================
# File: ESPN_Scraper_test.py
# Project: Sports_Betting
# File Created: Friday, 10th April 2020 11:25:21 am
# Author: Dillon Koch
# -----
# Last Modified: Friday, 10th April 2020 5:47:55 pm
# Modified By: Dillon Koch
# -----
#
#
# -----
# Testing the ESPN Scraper Class
# ==============================================================================
from unittest import TestCase

from ESPN_Scraper import ESPN_Scraper


class Test_ESPN_Scraper(TestCase):

    espn = ESPN_Scraper()
    nfl_game_id = "401128044"
    nfl_sp = espn._sp_helper("NFL", nfl_game_id)
    nba_game_id = "401160782"
    nba_sp = espn._sp_helper("NBA", nba_game_id)
    ncaaf_game_id = "401112199"
    ncaaf_sp = espn._sp_helper("NCAAF", ncaaf_game_id)
    hockey_game_id = "401146120"
    hockey_sp = espn._sp_helper("NHL", hockey_game_id)

    def setUp(self):
        self.espn = ESPN_Scraper()

    def test_nfl_team_names(self):
        home_name, away_name = self.espn._nfl_team_names(self.nfl_game_id, sp=self.nfl_sp)

        self.assertEqual("Cleveland Browns", home_name)
        self.assertEqual("Pittsburgh Steelers", away_name)

    def test_nfl_records(self):
        home_record, away_record = self.espn._nfl_records(self.nfl_game_id, sp=self.nfl_sp)

        self.assertEqual("4-6, 2-3 Home", home_record)
        self.assertEqual("5-5, 1-3 Away", away_record)

    def test_nfl_final_status(self):
        status = self.espn._nfl_final_status(self.nfl_game_id, sp=self.nfl_sp)

        self.assertEqual("Final", status)

    def test_nfl_quarter_scores(self):
        home_scores, away_scores = self.espn._nfl_quarter_scores(self.nfl_game_id, sp=self.nfl_sp)

        self.assertEqual(['7', '7', '0', '7'], home_scores)
        self.assertEqual(['0', '0', '7', '0'], away_scores)

    def test_nfl_scores(self):
        home_score, away_score = self.espn.nfl_scores(self.nfl_game_id, sp=self.nfl_sp)

        self.assertEqual(home_score, "21")
        self.assertEqual(away_score, "7")

    def test_nba_team_names(self):
        home_name, away_name = self.espn._nba_team_names(self.nba_game_id, sp=self.nba_sp)

        self.assertEqual("Detroit Pistons", home_name)
        self.assertEqual("Minnesota Timberwolves", away_name)

    def test_nba_records(self):
        home_record, away_record = self.espn._nba_records(self.nba_game_id, sp=self.nba_sp)

        self.assertEqual("4-7, 3-3 Home", home_record)
        self.assertEqual("6-4, 4-2 Away", away_record)

    def test_nba_final_status(self):
        status = self.espn._nba_final_status(self.nba_game_id, sp=self.nba_sp)

        self.assertEqual("Final", status)

    def test_nba_quarter_scores(self):
        home_qscores, away_qscores = self.espn._nba_quarter_scores(self.nba_game_id, sp=self.nba_sp)

        self.assertEqual(["41", "25", "26", "28"], away_qscores)
        self.assertEqual(["26", "25", "30", "33"], home_qscores)

    def test_nba_scores(self):
        home_score, away_score = self.espn.nba_scores(self.nba_game_id, self.nba_sp)

        self.assertEqual("114", home_score)
        self.assertEqual("120", away_score)

    def test_ncaaf_team_names(self):
        home_name, away_name = self.espn._ncaaf_team_names(self.ncaaf_game_id, self.ncaaf_sp)

        self.assertEqual("Iowa Hawkeyes", home_name)
        self.assertEqual("Minnesota Golden Gophers", away_name)

    def test_ncaaf_records(self):
        home_record, away_record = self.espn._ncaaf_records(self.ncaaf_game_id, self.ncaaf_sp)

        self.assertEqual("7-3, 4-3 Conf", home_record)
        self.assertEqual("9-1, 6-1 Conf", away_record)

    def test_ncaaf_final_status(self):
        status = self.espn._ncaaf_final_status(self.ncaaf_game_id, self.ncaaf_sp)

        self.assertEqual("Final", status)

    def test_ncaaf_scores(self):
        home_score, away_score = self.espn.ncaaf_scores(self.ncaaf_game_id, self.ncaaf_sp)

        self.assertEqual("23", home_score)
        self.assertEqual("19", away_score)

    def test_hockey_team_names(self):
        home_name, away_name = self.espn._hockey_team_names(self.hockey_game_id, sp=self.hockey_sp)

        self.assertEqual(home_name, "Chicago Blackhawks")
        self.assertEqual(away_name, "San Jose Sharks")

    def test_hockey_records(self):
        home_record, away_record = self.espn._hockey_records(self.hockey_game_id, sp=self.hockey_sp)

        self.assertEqual(home_record, "32-30-8")
        self.assertEqual(away_record, "29-36-5")

    def test_hockey_scores(self):
        home_score, away_score = self.espn.hockey_score(self.hockey_game_id, sp=self.hockey_sp)

        self.assertEqual(home_score, "6")
        self.assertEqual(away_score, "2")
