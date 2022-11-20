# ==============================================================================
# File: team_stats_scraper_test.py
# Project: Season_Scrapers
# File Created: Tuesday, 16th June 2020 4:44:31 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 2nd July 2020 5:15:41 pm
# Modified By: Dillon Koch
# -----
#
#
# -----
# Testing the team stats scraper
# ==============================================================================

import sys
from os.path import abspath, dirname
from unittest import TestCase


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN_Scrapers.team_stats_scraper import ESPN_Stat_Scraper, Team_Stats


class Test_ESPN_Stat_Scraper(TestCase):
    """
    Tests for both the Team_Stats object and ESPN_Stat_Scraper
    """
    nfl = ESPN_Stat_Scraper("NFL")
    nba = ESPN_Stat_Scraper("NBA")
    ncaaf = ESPN_Stat_Scraper("NCAAF")
    ncaab = ESPN_Stat_Scraper("NCAAB")

    def setUp(self):
        pass

    def test_football_bball_dict(self):
        ts = Team_Stats()
        fball = ts.football_dict
        bball = ts.basketball_dict
        for dic in [fball, bball]:
            self.assertIsInstance(dic, dict)
            for val in list(dic.values()):
                self.assertTrue(" " not in val)
                self.assertTrue(val in ts.__dict__.keys())

    def test_add_football_item(self):
        ts = Team_Stats()
        self.assertEqual(None, ts.passing_yards)
        ts.add_football_item("Passing Yards 300 400")
        self.assertEqual(["300", "400"], ts.passing_yards)

    def test_add_basketball_item(self):
        ts = Team_Stats()
        self.assertEqual(None, ts.rebounds)
        ts.add_basketball_item("Rebounds 45 53")
        self.assertEqual(["45", "53"], ts.rebounds)

    def test_add_row_nfl(self):
        ts = self.nfl.run('400874577')
        row = ts.make_row(football_league=True)
        true_row = ['21', '11',
                    '352', '214',
                    '240', '150',
                    '112', '64',
                    '8-69', '4-40',
                    '2', '0',
                    '34:32', '25:28',
                    '5-16', '3-14',
                    '2-3', '0-1',
                    '27-43', '16-29',
                    '5.2', '4.4',
                    '1', '0',
                    '32', '20',
                    '3.5', '3.2',
                    '1', '0',
                    '78', '54',
                    '12', '12',
                    '4.5', '4.0',
                    '1-2', '1-3',
                    '0', '0',
                    '16', '7',
                    '4', '3',
                    '1', '1',
                    '3-18', '5-36']
        self.assertEqual(true_row, row)

    def test_add_row_nba(self):
        ts = self.nba.run('401161604')
        row = ts.make_row(football_league=False)
        true_row = [
            '42-84', '40-80',
            '50.0', '50.0',
            '12-34', '6-24',
            '35.3', '25.0',
            '12-15', '17-23',
            '80.0', '73.9',
            '49', '42',
            '23', '29',
            '8', '9',
            '6', '5',
            '21', '18',
            '11', '11',
            '56', '66',
            '21', '15',
            '10', '4',
            '14', '9',
            '32', '26',
            '32', '20',
            '1', '1',
            '0', '0',
        ]
        self.assertEqual(true_row, row)

    def test_football_league(self):
        self.assertTrue(self.nfl.football_league)
        self.assertTrue(self.ncaaf.football_league)
        self.assertFalse(self.nba.football_league)
        self.assertFalse(self.ncaab.football_league)

    def test_results_nfl(self):
        ts = self.nfl.run('400874577')
        self.assertEqual(['11', '21'], ts.first_downs)
        self.assertEqual(['214', '352'], ts.total_yards)
        self.assertEqual(['150', '240'], ts.passing_yards)
        self.assertEqual(['64', '112'], ts.rushing_yards)
        self.assertEqual(['4-40', '8-69'], ts.penalties)
        self.assertEqual(['0', '2'], ts.turnovers)
        self.assertEqual(['25:28', '34:32'], ts.possession)
        self.assertEqual(['3-14', '5-16'], ts.third_down_eff)
        self.assertEqual(['0-1', '2-3'], ts.fourth_down_eff)
        self.assertEqual(['16-29', '27-43'], ts.completions_attempts)
        self.assertEqual(['4.4', '5.2'], ts.yards_per_pass)
        self.assertEqual(['0', '1'], ts.interceptions_thrown)
        self.assertEqual(['20', '32'], ts.rushing_attempts)
        self.assertEqual(['3.2', '3.5'], ts.yards_per_rush)
        self.assertEqual(['0', '1'], ts.fumbles_lost)
        self.assertEqual(['54', '78'], ts.total_plays)
        self.assertEqual(['12', '12'], ts.total_drives)
        self.assertEqual(['4.0', '4.5'], ts.yards_per_play)
        self.assertEqual(['1-3', '1-2'], ts.redzone_made_att)
        self.assertEqual(['0', '0'], ts.dst_touchdowns)
        self.assertEqual(['7', '16'], ts.passing_first_downs)
        self.assertEqual(['3', '4'], ts.rushing_first_downs)
        self.assertEqual(['1', '1'], ts.first_downs_from_penalties)
        self.assertEqual(['5-36', '3-18'], ts.sacks_yards_lost)

    def test_results_nba(self):
        ts = self.nba.run('401161604')
        self.assertEqual(['40-80', '42-84'], ts.field_goals)
        self.assertEqual(['50.0', '50.0'], ts.field_goal_pct)
        self.assertEqual(['6-24', '12-34'], ts.three_pointers)
        self.assertEqual(['25.0', '35.3'], ts.three_point_pct)
        self.assertEqual(['17-23', '12-15'], ts.free_throws)
        self.assertEqual(['73.9', '80.0'], ts.free_throw_pct)
        self.assertEqual(['42', '49'], ts.rebounds)
        self.assertEqual(['29', '23'], ts.assists)
        self.assertEqual(['9', '8'], ts.steals)
        self.assertEqual(['5', '6'], ts.blocks)
        self.assertEqual(['18', '21'], ts.total_turnovers)
        self.assertEqual(['11', '11'], ts.fast_break_points)
        self.assertEqual(['66', '56'], ts.points_in_paint)
        self.assertEqual(['15', '21'], ts.fouls)
        self.assertEqual(['4', '10'], ts.largest_lead)
        self.assertEqual(['9', '14'], ts.offensive_rebounds)
        self.assertEqual(['26', '32'], ts.defensive_rebounds)
        self.assertEqual(['20', '32'], ts.points_off_turnovers)
        self.assertEqual(['1', '1'], ts.technical_fouls)
        self.assertEqual(['0', '0'], ts.flagrant_fouls)

    def test_results_ncaaf(self):
        ts = self.ncaaf.run('401112199')
        self.assertEqual(['23', '17'], ts.first_downs)
        self.assertEqual(['7-14', '5-11'], ts.third_down_eff)
        self.assertEqual(['1-3', '1-1'], ts.fourth_down_eff)
        self.assertEqual(['431', '290'], ts.total_yards)
        self.assertEqual(['368', '173'], ts.passing_yards)
        self.assertEqual(['25-39', '14-23'], ts.completions_attempts)
        self.assertEqual(['9.4', '7.5'], ts.yards_per_pass)
        self.assertEqual(['1', '0'], ts.interceptions_thrown)
        self.assertEqual(['63', '117'], ts.rushing_yards)
        self.assertEqual(['30', '31'], ts.rushing_attempts)
        self.assertEqual(['2.1', '3.8'], ts.yards_per_rush)
        self.assertEqual(['5-52', '3-16'], ts.penalties)
        self.assertEqual(['1', '0'], ts.turnovers)
        self.assertEqual(['0', '0'], ts.fumbles_lost)
        self.assertEqual(['1', '0'], ts.interceptions_thrown)
        self.assertEqual(['32:20', '27:40'], ts.possession)

    def test_results_ncaab(self):
        ts = self.ncaab.run('401211587')
        self.assertEqual(['24-63', '22-47'], ts.field_goals)
        self.assertEqual(['38.1', '46.8'], ts.field_goal_pct)
        self.assertEqual(['11-36', '7-22'], ts.three_pointers)
        self.assertEqual(['30.6', '31.8'], ts.three_point_pct)
        self.assertEqual(['5-7', '18-19'], ts.free_throws)
        self.assertEqual(['71.4', '94.7'], ts.free_throw_pct)
        self.assertEqual(['34', '32'], ts.rebounds)
        self.assertEqual(['12', '4'], ts.offensive_rebounds)
        self.assertEqual(['22', '28'], ts.defensive_rebounds)
        self.assertEqual(['6', '11'], ts.assists)
        self.assertEqual(['7', '5'], ts.steals)
        self.assertEqual(['3', '1'], ts.blocks)
        self.assertEqual(['10', '11'], ts.total_turnovers)
        self.assertEqual(['16', '10'], ts.fouls)
        self.assertEqual(['0', '0'], ts.technical_fouls)
        self.assertEqual(['4', '11'], ts.largest_lead)
