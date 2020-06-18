# ==============================================================================
# File: team_stats_scraper_test.py
# Project: Season_Scrapers
# File Created: Tuesday, 16th June 2020 4:44:31 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 16th June 2020 5:39:56 pm
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

from Season_Scrapers.team_stats_scraper import ESPN_Stat_Scraper


class Test_ESPN_Stat_Scraper(TestCase):
    nfl = ESPN_Stat_Scraper("NFL")
    nba = ESPN_Stat_Scraper("NBA")
    ncaaf = ESPN_Stat_Scraper("NCAAF")
    ncaab = ESPN_Stat_Scraper("NCAAB")

    def setUp(self):
        pass

    def test_football_league(self):
        self.assertTrue(self.nfl.football_league)
        self.assertTrue(self.ncaaf.football_league)
        self.assertFalse(self.nba.football_league)
        self.assertFalse(self.ncaab.football_league)

    def test_results_nfl(self):
        ts = self.nfl.run('400874577')
        self.assertEqual(['11', '21'], ts.first_downs)
        self.assertEqual(['7', '16'], ts.passing_first_downs)
        self.assertEqual(['3', '4'], ts.rushing_first_downs)
        self.assertEqual(['1', '1'], ts.first_downs_from_penalties)
        self.assertEqual(['3-14', '5-16'], ts.third_down_eff)
        self.assertEqual(['0-1', '2-3'], ts.fourth_down_eff)
        self.assertEqual(['54', '78'], ts.total_plays)
        self.assertEqual(['214', '352'], ts.total_yards)
        self.assertEqual(['12', '12'], ts.total_drives)
        self.assertEqual(['4.0', '4.5'], ts.yards_per_play)
        self.assertEqual(['150', '240'], ts.passing_yards)
        self.assertEqual(['16-29', '27-43'], ts.completions_attempts)
        self.assertEqual(['4.4', '5.2'], ts.yards_per_pass)
        self.assertEqual(['0', '1'], ts.interceptions_thrown)
        self.assertEqual(['5-36', '3-18'], ts.sacks_yards_lost)
        self.assertEqual(['64', '112'], ts.rushing_yards)
        self.assertEqual(['20', '32'], ts.rushing_attempts)
        self.assertEqual(['3.2', '3.5'], ts.yards_per_rush)
        self.assertEqual(['1-3', '1-2'], ts.redzone_made_att)
        self.assertEqual(['4-40', '8-69'], ts.penalties)
        self.assertEqual(['0', '2'], ts.turnovers)
        self.assertEqual(['0', '1'], ts.fumbles_lost)
        self.assertEqual(['0', '1'], ts.interceptions_thrown)
        self.assertEqual(['0', '0'], ts.dst_touchdowns)
        self.assertEqual(['25:28', '34:32'], ts.possession)

    def test_results_nba(self):
        ts = self.nba.run('401161604')
        self.assertEqual(['40-80', '42-84'], ts.field_goals)
        self.assertEqual(['50.0', '50.0'], ts.field_goal_pct)
        self.assertEqual(['6-24', '12-34'], ts.three_pointers)
        self.assertEqual(['25.0', '35.3'], ts.three_point_pct)
        self.assertEqual(['17-23', '12-15'], ts.free_throws)
        self.assertEqual(['73.9', '80.0'], ts.free_throw_pct)
        self.assertEqual(['42', '49'], ts.rebounds)
        self.assertEqual(['9', '14'], ts.offensive_rebounds)
        self.assertEqual(['26', '32'], ts.defensive_rebounds)
        self.assertEqual(['29', '23'], ts.assists)
        self.assertEqual(['9', '8'], ts.steals)
        self.assertEqual(['5', '6'], ts.blocks)
        self.assertEqual(['18', '21'], ts.total_turnovers)
        self.assertEqual(['20', '32'], ts.points_off_turnovers)
        self.assertEqual(['11', '11'], ts.fast_break_points)
        self.assertEqual(['66', '56'], ts.points_in_paint)
        self.assertEqual(['15', '21'], ts.fouls)
        self.assertEqual(['1', '1'], ts.technical_fouls)
        self.assertEqual(['0', '0'], ts.flagrant_fouls)
        self.assertEqual(['4', '10'], ts.largest_lead)

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
        ts = self.ncaab.run('401170371')
        self.assertEqual(['23-52', '30-64'], ts.field_goals)
        self.assertEqual(['44.2', '46.9'], ts.field_goal_pct)
        self.assertEqual(['5-16', '6-19'], ts.three_pointers)
        self.assertEqual(['31.3', '31.6'], ts.three_point_pct)
        self.assertEqual(['19-30', '6-10'], ts.free_throws)
        self.assertEqual(['63.3', '60.0'], ts.free_throw_pct)
        self.assertEqual(['36', '34'], ts.rebounds)
        self.assertEqual(['11', '11'], ts.offensive_rebounds)
        self.assertEqual(['25', '23'], ts.defensive_rebounds)
        self.assertEqual(['9', '12'], ts.assists)
        self.assertEqual(['9', '14'], ts.steals)
        self.assertEqual(['2', '4'], ts.blocks)
        self.assertEqual(['22', '21'], ts.total_turnovers)
        self.assertEqual(['17', '25'], ts.fouls)
        self.assertEqual(['1', '1'], ts.technical_fouls)
        self.assertEqual(['19', '3'], ts.largest_lead)
