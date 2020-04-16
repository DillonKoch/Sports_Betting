# ==============================================================================
# File: espn_game_scraper_test.py
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
# Testing the ESPN Game Scraper Class
# ==============================================================================
from unittest import TestCase

from espn_game_scraper import ESPN_Game_Scraper


class Test_ESPN_Game_Scraper(TestCase):

    espn = ESPN_Game_Scraper()
    nfl_game_id = "401128044"
    nfl_sp = espn._sp_helper("NFL", nfl_game_id)
    nba_game_id = "401160782"
    nba_sp = espn._sp_helper("NBA", nba_game_id)
    ncaaf_game_id = "401112199"
    ncaaf_sp = espn._sp_helper("NCAAF", ncaaf_game_id)
    ncaab_game_id = "401166198"
    ncaab_sp = espn._sp_helper("NCAAB", ncaab_game_id)
    hockey_game_id = "401146120"
    hockey_sp = espn._sp_helper("NHL", hockey_game_id)

    def setUp(self):
        self.espn = ESPN_Game_Scraper()

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

    def test_nfl_overtime_quarter_scores(self):
        home_scores, away_scores = self.espn._nfl_quarter_scores("401127972")

        self.assertEqual(['7', '10', '7', '0', '6'], home_scores)
        self.assertEqual(['0', '6', '10', '8', '0'], away_scores)

    def test_nfl_scores(self):
        home_score, away_score = self.espn.nfl_scores(self.nfl_game_id, sp=self.nfl_sp)

        self.assertEqual("21", home_score)
        self.assertEqual("7", away_score)

    def test_nfl_game_network(self):
        network = self.espn._nfl_game_network(self.nfl_game_id, sp=self.nfl_sp)

        self.assertEqual("FOX/NFL", network)

    def test_nfl_line_ou(self):
        line, over_under = self.espn._nfl_line_ou(self.nfl_game_id, sp=self.nfl_sp)

        self.assertEqual("CLE -3.0", line)
        self.assertEqual("42", over_under)

    def test_all_nfl_info(self):
        game = self.espn.all_nfl_info(self.nfl_game_id, sp=self.nfl_sp)
        self.assertEqual(self.nfl_game_id, game.ESPN_ID)
        self.assertEqual("Cleveland Browns", game.home_name)
        self.assertEqual("Pittsburgh Steelers", game.away_name)
        self.assertEqual("4-6, 2-3 Home", game.home_record)
        self.assertEqual("5-5, 1-3 Away", game.away_record)
        self.assertEqual("Final", game.final_status)
        self.assertEqual(['7', '7', '0', '7'], game.home_qscores)
        self.assertEqual(['0', '0', '7', '0'], game.away_qscores)
        self.assertEqual("21", game.home_score)
        self.assertEqual("7", game.away_score)
        self.assertEqual("FOX/NFL", game.network)
        self.assertEqual("CLE -3.0", game.line)
        self.assertEqual("42", game.over_under)

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

    def test_nba_overtime_quarter_scores(self):
        home_scores, away_scores = self.espn._nba_quarter_scores("401161460")

        self.assertEqual(["32", "26", "29", "27", "19"], away_scores)
        self.assertEqual(["30", "30", "31", "23", "27"], home_scores)

    def test_nba_scores(self):
        home_score, away_score = self.espn.nba_scores(self.nba_game_id, self.nba_sp)

        self.assertEqual("114", home_score)
        self.assertEqual("120", away_score)

    def test_nba_game_network(self):
        network = self.espn._nba_game_network("401160624")

        self.assertEqual("TNT", network)

    def test_nba_line_ou(self):
        line, over_under = self.espn._nba_line_ou(self.nba_game_id, self.nba_sp)

        self.assertEqual("DET -4.0", line)
        self.assertEqual("223", over_under)

    def test_all_nba_info(self):
        game = self.espn.all_nba_info(self.nba_game_id, self.nba_sp)
        self.assertEqual(self.nba_game_id, game.ESPN_ID)
        self.assertEqual("Detroit Pistons", game.home_name)
        self.assertEqual("Minnesota Timberwolves", game.away_name)
        self.assertEqual("4-7, 3-3 Home", game.home_record)
        self.assertEqual("6-4, 4-2 Away", game.away_record)
        self.assertEqual("Final", game.final_status)
        self.assertEqual(["41", "25", "26", "28"], game.away_qscores)
        self.assertEqual(["26", "25", "30", "33"], game.home_qscores)
        self.assertEqual("114", game.home_score)
        self.assertEqual("120", game.away_score)
        self.assertEqual("DET -4.0", game.line)
        self.assertEqual("223", game.over_under)

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

    def test_ncaaf_quarter_scores(self):
        home_qscores, away_qscores = self.espn._ncaaf_quarter_scores(self.ncaaf_game_id, self.ncaaf_sp)

        self.assertEqual(['13', '7', '0', '3'], home_qscores)
        self.assertEqual(['0', '6', '7', '6'], away_qscores)

    def test_overtime_ncaaf_quarter_scores(self):
        home_scores, away_scores = self.espn._ncaaf_quarter_scores("401112085")

        self.assertEqual(["3", "0", "7", "3", "16"], home_scores)
        self.assertEqual(["0", "0", "13", "0", "13"], away_scores)

    def test_ncaaf_scores(self):
        home_score, away_score = self.espn.ncaaf_scores(self.ncaaf_game_id, self.ncaaf_sp)

        self.assertEqual("23", home_score)
        self.assertEqual("19", away_score)

    def test_ncaaf_game_netowrk(self):
        network = self.espn._ncaaf_game_netowrk(self.ncaaf_game_id, self.ncaaf_sp)

        self.assertEqual("FOX", network)

    def test_ncaaf_line_ou(self):
        line, over_under = self.espn._ncaaf_line_ou(self.ncaaf_game_id, self.ncaaf_sp)

        self.assertEqual("IOWA -3.0", line)
        self.assertEqual("45", over_under)

    def test_all_ncaaf_info(self):
        game = self.espn.all_ncaaf_info(self.ncaaf_game_id, self.ncaaf_sp)
        self.assertEqual(self.ncaaf_game_id, game.ESPN_ID)
        self.assertEqual("Iowa Hawkeyes", game.home_name)
        self.assertEqual("Minnesota Golden Gophers", game.away_name)
        self.assertEqual("7-3, 4-3 Conf", game.home_record)
        self.assertEqual("9-1, 6-1 Conf", game.away_record)
        self.assertEqual("Final", game.final_status)
        self.assertEqual(['13', '7', '0', '3'], game.home_qscores)
        self.assertEqual(['0', '6', '7', '6'], game.away_qscores)
        self.assertEqual("23", game.home_score)
        self.assertEqual("19", game.away_score)
        self.assertEqual("IOWA -3.0", game.line)
        self.assertEqual("45", game.over_under)

    def test_ncaab_team_names(self):
        home_name, away_name = self.espn._ncaab_team_names(self.ncaab_game_id, self.ncaab_sp)

        self.assertEqual("Illinois Fighting Illini", home_name)
        self.assertEqual("Minnesota Golden Gophers", away_name)

    def test_ncaab_records(self):
        home_record, away_record = self.espn._ncaab_records(self.ncaab_game_id, self.ncaab_sp)

        self.assertEqual("16-5, 8-2 Conf", home_record)
        self.assertEqual("11-10, 5-6 Conf", away_record)

    def test_ncaab_final_status(self):
        status = self.espn._ncaab_final_status(self.ncaab_game_id, self.ncaab_sp)

        self.assertEqual("Final", status)

    def test_ncaab_half_scores(self):
        home_half_scores, away_half_scores = self.espn._ncaab_half_scores(self.ncaab_game_id, self.ncaab_sp)

        self.assertEqual(['20', '31'], away_half_scores)
        self.assertEqual(['24', '35'], home_half_scores)

    def test_overtime_ncaab_half_scores(self):
        home_half_scores, away_half_scores = self.espn._ncaab_half_scores("400915005")

        self.assertEqual(["39", "35", "12"], home_half_scores)
        self.assertEqual(["36", "38", "9"], away_half_scores)

    def test_ncaab_scores(self):
        home_score, away_score = self.espn.ncaab_scores(self.ncaab_game_id, self.ncaab_sp)

        self.assertEqual("59", home_score)
        self.assertEqual("51", away_score)

    def test_ncaab_game_network(self):
        network = self.espn._ncaab_game_network(self.ncaab_game_id, self.ncaab_sp)

        self.assertEqual("FS1", network)

    def test_ncaab_line_ou(self):
        line, over_under = self.espn._ncaab_line_ou(self.ncaab_game_id, self.ncaab_sp)

        self.assertEqual("ILL -6.0", line)
        self.assertEqual("135", over_under)

    def test_all_ncaab_info(self):
        game = self.espn.all_ncaab_info(self.ncaab_game_id, self.ncaab_sp)
        self.assertEqual(self.ncaab_game_id, game.ESPN_ID)
        self.assertEqual("Illinois Fighting Illini", game.home_name)
        self.assertEqual("Minnesota Golden Gophers", game.away_name)
        self.assertEqual("16-5, 8-2 Conf", game.home_record)
        self.assertEqual("11-10, 5-6 Conf", game.away_record)
        self.assertEqual("Final", game.final_status)
        self.assertEqual(['20', '31'], game.away_half_scores)
        self.assertEqual(['24', '35'], game.home_half_scores)
        self.assertEqual("59", game.home_score)
        self.assertEqual("51", game.away_score)
        self.assertEqual("ILL -6.0", game.line)
        self.assertEqual("135", game.over_under)

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
