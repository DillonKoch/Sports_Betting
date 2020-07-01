# ==============================================================================
# File: espn_game_scraper_test2.py
# Project: Tests
# File Created: Wednesday, 1st July 2020 9:23:53 am
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 1st July 2020 10:32:00 am
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
        home_score, away_score = self.nfl.game_scores(self.nfl_game_id, sp=self.nfl_sp)
        self.assertEqual("21", home_score)
        self.assertEqual("7", away_score)

        home_score, away_score = self.nfl.game_scores("4011579")
        self.assertEqual(None, home_score)
        self.assertEqual(None, away_score)

    def test_nfl_line_ou(self):
        line, over_under = self.nfl.line_over_under(self.nfl_game_id, sp=self.nfl_sp)
        self.assertEqual("CLE -3.0", line)
        self.assertEqual("42", over_under)

        line, over_under = self.nfl.line_over_under("298374930")
        self.assertEqual(None, line)
        self.assertEqual(None, over_under)

    def test_nfl_game_network(self):
        network = self.nfl.game_network(self.nfl_game_id, sp=self.nfl_sp)
        self.assertEqual("FOX/NFL", network)

        network = self.nfl.game_network("401283229")
        self.assertEqual(None, network)

    def test_nfl_game_date(self):
        game_date = self.nfl.game_date(self.nfl_game_id, sp=self.nfl_sp)
        self.assertEqual('November 14, 2019', game_date)

    def test_all_nfl_info(self):
        game = self.nfl.run(self.nfl_game_id, sp=self.nfl_sp)
        self.assertEqual(self.nfl_game_id, game.ESPN_ID)
        self.assertEqual("Cleveland Browns", game.home_name)
        self.assertEqual("Pittsburgh Steelers", game.away_name)
        self.assertEqual("4-6, 2-3 Home", game.home_record)
        self.assertEqual("5-5, 1-3 Away", game.away_record)
        self.assertEqual("Final", game.final_status)
        self.assertEqual(['7', '7', '0', '7', None], game.home_qscores)
        self.assertEqual(['0', '0', '7', '0', None], game.away_qscores)
        self.assertEqual("21", game.home_score)
        self.assertEqual("7", game.away_score)
        self.assertEqual("FOX/NFL", game.network)
        self.assertEqual("CLE -3.0", game.line)
        self.assertEqual("42", game.over_under)
        self.assertEqual("November 14, 2019", game.game_date)

    def test_nba_team_names(self):
        home_name, away_name = self.nba.team_names(self.nba_game_id, sp=self.nba_sp)
        self.assertEqual("Detroit Pistons", home_name)
        self.assertEqual("Minnesota Timberwolves", away_name)

        home_name, away_name = self.nba.team_names("4011asnvisd")
        self.assertEqual(None, home_name)
        self.assertEqual(None, away_name)

    def test_nba_records(self):
        home_record, away_record = self.nba.team_records(self.nba_game_id, sp=self.nba_sp)
        self.assertEqual("4-7, 3-3 Home", home_record)
        self.assertEqual("6-4, 4-2 Away", away_record)

        home_record, away_record = self.nba.team_records("40119999999")
        self.assertEqual(None, home_record)
        self.assertEqual(None, away_record)

    def test_nba_final_status(self):
        status = self.nba.final_status(self.nba_game_id, sp=self.nba_sp)
        self.assertEqual("Final", status)

        status = self.nba.final_status("40112983789")
        self.assertEqual(None, status)

    def test_nba_quarter_scores(self):
        home_qscores, away_qscores = self.nba.quarter_scores(self.nba_game_id, sp=self.nba_sp)
        self.assertEqual(["41", "25", "26", "28", None], away_qscores)
        self.assertEqual(["26", "25", "30", "33", None], home_qscores)

        home_scores, away_scores = self.nba.quarter_scores("09a789798326")
        none_result = [None] * 5
        self.assertEqual(none_result, home_scores)
        self.assertEqual(none_result, away_scores)

    def test_nba_overtime_quarter_scores(self):
        home_scores, away_scores = self.nba.quarter_scores("401161460")
        self.assertEqual(["32", "26", "29", "27", "19"], away_scores)
        self.assertEqual(["30", "30", "31", "23", "27"], home_scores)

        home_scores, away_scores = self.nba.quarter_scores("asdvndk")
        none_result = [None] * 5
        self.assertEqual(none_result, home_scores)
        self.assertEqual(none_result, away_scores)

    def test_nba_scores(self):
        home_score, away_score = self.nba.game_scores(self.nba_game_id, self.nba_sp)
        self.assertEqual("114", home_score)
        self.assertEqual("120", away_score)

        home_score, away_score = self.nba.game_scores("4011579")
        self.assertEqual(None, home_score)
        self.assertEqual(None, away_score)

    def test_nba_game_network(self):
        network = self.nba.game_network("401160624")
        self.assertEqual("TNT", network)

        network = self.nba.game_network("401283229")
        self.assertEqual(None, network)

    def test_nba_line_ou(self):
        line, over_under = self.nba.line_over_under(self.nba_game_id, self.nba_sp)
        self.assertEqual("DET -4.0", line)
        self.assertEqual("223", over_under)

        line, over_under = self.nba.line_over_under("298374930")
        self.assertEqual(None, line)
        self.assertEqual(None, over_under)

    def test_nba_game_date(self):
        date = self.nba.game_date(self.nba_game_id, self.nba_sp)
        self.assertEqual('November 11, 2019', date)

        date = self.nba.game_date("1290dj2190")
        self.assertEqual(None, date)

    def test_all_nba_info(self):
        game = self.nba.run(self.nba_game_id, self.nba_sp)
        self.assertEqual(self.nba_game_id, game.ESPN_ID)
        self.assertEqual("Detroit Pistons", game.home_name)
        self.assertEqual("Minnesota Timberwolves", game.away_name)
        self.assertEqual("4-7, 3-3 Home", game.home_record)
        self.assertEqual("6-4, 4-2 Away", game.away_record)
        self.assertEqual("Final", game.final_status)
        self.assertEqual(["41", "25", "26", "28", None], game.away_qscores)
        self.assertEqual(["26", "25", "30", "33", None], game.home_qscores)
        self.assertEqual("114", game.home_score)
        self.assertEqual("120", game.away_score)
        self.assertEqual(None, game.network)
        self.assertEqual("DET -4.0", game.line)
        self.assertEqual("223", game.over_under)
        self.assertEqual("November 11, 2019", game.game_date)

    def test_ncaaf_team_names(self):
        home_name, away_name = self.ncaaf.team_names(self.ncaaf_game_id, self.ncaaf_sp)
        self.assertEqual("Iowa Hawkeyes", home_name)
        self.assertEqual("Minnesota Golden Gophers", away_name)

        home_name, away_name = self.ncaaf.team_names("4011asnvisd")
        self.assertEqual(None, home_name)
        self.assertEqual(None, away_name)

    def test_ncaaf_records(self):
        home_record, away_record = self.ncaaf.team_records(self.ncaaf_game_id, self.ncaaf_sp)
        self.assertEqual("7-3, 4-3 Conf", home_record)
        self.assertEqual("9-1, 6-1 Conf", away_record)

        home_record, away_record = self.ncaaf.team_records("40119999999")
        self.assertEqual(None, home_record)
        self.assertEqual(None, away_record)

    def test_ncaaf_final_status(self):
        status = self.ncaaf.final_status(self.ncaaf_game_id, self.ncaaf_sp)
        self.assertEqual("Final", status)

        status = self.ncaaf.final_status("40112983789")
        self.assertEqual(None, status)

    def test_ncaaf_quarter_scores(self):
        home_qscores, away_qscores = self.ncaaf.quarter_scores(self.ncaaf_game_id, self.ncaaf_sp)
        self.assertEqual(['13', '7', '0', '3', None], home_qscores)
        self.assertEqual(['0', '6', '7', '6', None], away_qscores)

        home_scores, away_scores = self.ncaaf.quarter_scores("09a789798326")
        none_result = [None] * 5
        self.assertEqual(none_result, home_scores)
        self.assertEqual(none_result, away_scores)

    def test_overtime_ncaafquarter_scores(self):
        home_scores, away_scores = self.ncaaf.quarter_scores("401112085")
        self.assertEqual(["3", "0", "7", "3", "16"], home_scores)
        self.assertEqual(["0", "0", "13", "0", "13"], away_scores)

        home_scores, away_scores = self.ncaaf.quarter_scores("asdvndk")
        none_result = [None] * 5
        self.assertEqual(none_result, home_scores)
        self.assertEqual(none_result, away_scores)

    def test_ncaaf_scores(self):
        home_score, away_score = self.ncaaf.game_scores(self.ncaaf_game_id, self.ncaaf_sp)
        self.assertEqual("23", home_score)
        self.assertEqual("19", away_score)

        home_score, away_score = self.ncaaf.game_scores("4011579")
        self.assertEqual(None, home_score)
        self.assertEqual(None, away_score)

    def test_ncaaf_game_network(self):
        network = self.ncaaf.game_network(self.ncaaf_game_id, self.ncaaf_sp)
        self.assertEqual("FOX", network)

        network = self.ncaaf.game_network("401283229")
        self.assertEqual(None, network)

    def test_ncaaf_line_over_under(self):
        line, over_under = self.ncaaf.line_over_under(self.ncaaf_game_id, self.ncaaf_sp)
        self.assertEqual("IOWA -3.0", line)
        self.assertEqual("45", over_under)

        line, over_under = self.ncaaf.line_over_under("298374930")
        self.assertEqual(None, line)
        self.assertEqual(None, over_under)

    def test_ncaaf_game_date(self):
        date = self.ncaaf.game_date(self.ncaaf_game_id, self.ncaaf_sp)
        self.assertEqual('November 16, 2019', date)

        date = self.ncaaf.game_date("98457295")
        self.assertEqual(None, date)

    def test_all_ncaaf_info(self):
        game = self.ncaaf.run(self.ncaaf_game_id, self.ncaaf_sp)
        self.assertEqual(self.ncaaf_game_id, game.ESPN_ID)
        self.assertEqual("Iowa Hawkeyes", game.home_name)
        self.assertEqual("Minnesota Golden Gophers", game.away_name)
        self.assertEqual("7-3, 4-3 Conf", game.home_record)
        self.assertEqual("9-1, 6-1 Conf", game.away_record)
        self.assertEqual("Final", game.final_status)
        self.assertEqual(['13', '7', '0', '3', None], game.home_qscores)
        self.assertEqual(['0', '6', '7', '6', None], game.away_qscores)
        self.assertEqual("23", game.home_score)
        self.assertEqual("19", game.away_score)
        self.assertEqual("FOX", game.network)
        self.assertEqual("IOWA -3.0", game.line)
        self.assertEqual("45", game.over_under)
        self.assertEqual("November 16, 2019", game.game_date)

    def test_ncaab_team_names(self):
        home_name, away_name = self.ncaab.team_names(self.ncaab_game_id, self.ncaab_sp)
        self.assertEqual("Illinois Fighting Illini", home_name)
        self.assertEqual("Minnesota Golden Gophers", away_name)

        home_name, away_name = self.ncaab.team_names("4011asnvisd")
        self.assertEqual(None, home_name)
        self.assertEqual(None, away_name)

    def test_ncaab_records(self):
        home_record, away_record = self.ncaab.team_records(self.ncaab_game_id, self.ncaab_sp)
        self.assertEqual("16-5, 8-2 Conf", home_record)
        self.assertEqual("11-10, 5-6 Conf", away_record)

        home_record, away_record = self.ncaab.team_records("40119999999")
        self.assertEqual(None, home_record)
        self.assertEqual(None, away_record)

    def test_ncaab_final_status(self):
        status = self.ncaab.final_status(self.ncaab_game_id, self.ncaab_sp)
        self.assertEqual("Final", status)

        status = self.ncaab.final_status("40112983789")
        self.assertEqual(None, status)

    def test_ncaab_half_scores(self):
        home_half_scores, away_half_scores = self.ncaab.half_scores(self.ncaab_game_id, self.ncaab_sp)
        self.assertEqual(['20', '31', None], away_half_scores)
        self.assertEqual(['24', '35', None], home_half_scores)

        home_scores, away_scores = self.ncaab.half_scores("asdvndk")
        none_result = [None] * 3
        self.assertEqual(none_result, home_scores)
        self.assertEqual(none_result, away_scores)

    def test_overtime_ncaab_half_scores(self):
        home_half_scores, away_half_scores = self.ncaab.half_scores("400915005")
        self.assertEqual(["39", "35", "12"], home_half_scores)
        self.assertEqual(["36", "38", "9"], away_half_scores)

        home_scores, away_scores = self.ncaab.half_scores("asdvndk")
        none_result = [None] * 3
        self.assertEqual(none_result, home_scores)
        self.assertEqual(none_result, away_scores)

    def test_ncaab_scores(self):
        home_score, away_score = self.ncaab.game_scores(self.ncaab_game_id, self.ncaab_sp)
        self.assertEqual("59", home_score)
        self.assertEqual("51", away_score)

        home_score, away_score = self.ncaab.game_scores("4011579")
        self.assertEqual(None, home_score)
        self.assertEqual(None, away_score)

    def test_ncaab_game_network(self):
        network = self.ncaab.game_network(self.ncaab_game_id, self.ncaab_sp)
        self.assertEqual("FS1", network)

        network = self.ncaab.game_network("401283229")
        self.assertEqual(None, network)

    def test_ncaabline_over_under(self):
        line, over_under = self.ncaab.line_over_under(self.ncaab_game_id, self.ncaab_sp)
        self.assertEqual("ILL -6.0", line)
        self.assertEqual("135", over_under)

        line, over_under = self.ncaab.line_over_under("298374930")
        self.assertEqual(None, line)
        self.assertEqual(None, over_under)

    def test_ncaabgame_date(self):
        date = self.ncaab.game_date(self.ncaab_game_id, self.ncaab_sp)
        self.assertEqual("January 30, 2020", date)

        date = self.ncaab.game_date("40148220932")
        self.assertEqual(None, date)

    def test_all_ncaab_info(self):
        game = self.ncaab.run(self.ncaab_game_id, self.ncaab_sp)
        self.assertEqual(self.ncaab_game_id, game.ESPN_ID)
        self.assertEqual("Illinois Fighting Illini", game.home_name)
        self.assertEqual("Minnesota Golden Gophers", game.away_name)
        self.assertEqual("16-5, 8-2 Conf", game.home_record)
        self.assertEqual("11-10, 5-6 Conf", game.away_record)
        self.assertEqual("Final", game.final_status)
        self.assertEqual(['20', '31', None], game.away_half_scores)
        self.assertEqual(['24', '35', None], game.home_half_scores)
        self.assertEqual("59", game.home_score)
        self.assertEqual("51", game.away_score)
        self.assertEqual("ILL -6.0", game.line)
        self.assertEqual("135", game.over_under)
        self.assertEqual("January 30, 2020", game.game_date)
