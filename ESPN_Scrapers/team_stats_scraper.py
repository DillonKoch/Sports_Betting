# ==============================================================================
# File: team_stats_scraper.py
# Project: Season_Scrapers
# File Created: Tuesday, 16th June 2020 1:42:34 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 28th July 2020 11:29:01 am
# Modified By: Dillon Koch
# -----
#
# -----
# Scraper to get the team stats for each game on ESPN
# ==============================================================================


import os
import sys
import time
from os.path import abspath, dirname
import datetime
import argparse

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.Utility import get_sp1, listdir_fullpath


class Team_Stats:
    def __init__(self):
        # Football
        self.first_downs = None
        self.total_yards = None
        self.passing_yards = None
        self.rushing_yards = None
        self.penalties = None
        self.turnovers = None
        self.possession = None
        self.third_down_eff = None
        self.fourth_down_eff = None
        self.completions_attempts = None
        self.yards_per_pass = None
        self.interceptions_thrown = None
        self.rushing_attempts = None
        self.yards_per_rush = None
        self.fumbles_lost = None
        self.total_plays = None
        self.total_drives = None
        self.yards_per_play = None
        self.redzone_made_att = None
        self.dst_touchdowns = None
        self.passing_first_downs = None
        self.rushing_first_downs = None
        self.first_downs_from_penalties = None
        self.sacks_yards_lost = None
        # Basketball
        self.field_goals = None
        self.field_goal_pct = None
        self.three_pointers = None
        self.three_point_pct = None
        self.free_throws = None
        self.free_throw_pct = None
        self.rebounds = None
        self.offensive_rebounds = None
        self.defensive_rebounds = None
        self.assists = None
        self.steals = None
        self.blocks = None
        self.total_turnovers = None
        self.points_off_turnovers = None
        self.fast_break_points = None
        self.points_in_paint = None
        self.fouls = None
        self.technical_fouls = None
        self.flagrant_fouls = None
        self.largest_lead = None

    def all_cols(self, football_league: bool):
        cols = list(self.football_dict.values()) if football_league else list(self.basketball_dict.values())
        all_cols = ["home_" + col if i % 2 == 0 else "away_" + col for i,
                    col in enumerate([col for col in cols for i in range(2)])]
        return all_cols

    @property
    def football_dict(self):  # Property
        football_dict = {
            "1st Downs": "first_downs",
            "Total Yards": "total_yards",
            "Passing": "passing_yards",
            "Rushing": "rushing_yards",
            "Penalties": "penalties",
            "Turnovers": "turnovers",
            "Possession": "possession",
            "3rd down efficiency": "third_down_eff",
            "4th down efficiency": "fourth_down_eff",
            "Comp-Att": "completions_attempts",
            "Yards per pass": "yards_per_pass",
            "Interceptions thrown": "interceptions_thrown",
            "Rushing Attempts": "rushing_attempts",
            "Yards per rush": "yards_per_rush",
            "Fumbles lost": "fumbles_lost",
            "Total Plays": "total_plays",
            "Total Drives": "total_drives",
            "Yards per Play": "yards_per_play",
            "Red Zone (Made-Att)": "redzone_made_att",
            "Defensive / Special Teams TDs": "dst_touchdowns",
            "Passing 1st downs": "passing_first_downs",
            "Rushing 1st downs": "rushing_first_downs",
            "1st downs from penalties": "first_downs_from_penalties",
            "Sacks-Yards Lost": "sacks_yards_lost"
        }
        return football_dict

    @property
    def basketball_dict(self):  # Property
        basketball_dict = {
            "FG": "field_goals",
            "Field Goal %": "field_goal_pct",
            "3PT": "three_pointers",
            "Three Point %": "three_point_pct",
            "FT": "free_throws",
            "Free Throw %": "free_throw_pct",
            "Rebounds": "rebounds",
            "Assists": "assists",
            "Steals": "steals",
            "Blocks": "blocks",
            "Total Turnovers": "total_turnovers",
            "Fast Break Points": "fast_break_points",
            "Points in Paint": "points_in_paint",
            "Fouls": "fouls",
            "Largest Lead": "largest_lead",
            "Offensive Rebounds": "offensive_rebounds",
            "Defensive Rebounds": "defensive_rebounds",
            "Points Off Turnovers": "points_off_turnovers",
            "Technical Fouls": "technical_fouls",
            "Flagrant Fouls": "flagrant_fouls"
        }
        return basketball_dict

    def make_row(self, football_league: bool):  # Run
        """
        Creates a list of the object's stats attributes to be inserted into a df row,
        works for either football (if football_league=True) or basketball
        """
        cols = list(self.basketball_dict.values()) if not football_league else list(self.football_dict.values())
        row = []
        for col in cols:
            away_val = self.__dict__[col][0] if self.__dict__[col] is not None else None
            home_val = self.__dict__[col][1] if self.__dict__[col] is not None else None
            row += [home_val, away_val]
        return row

    def add_football_item(self, stat_string: str):  # Run  Tested
        """
        adds a football stat string to the Team Stats object's attributes using __dict__
        stat is in format "Passing Yards 300 400" -> self.passing_yards = ["300", "400"]
        """
        football_keys = list(self.football_dict.keys())
        values = stat_string.split(' ')[-2:]
        matches = []
        for item in football_keys:
            if item in stat_string:
                matches.append(item)
        if len(matches) > 0:
            update_key = self.football_dict[max(matches, key=len)]
            self.__dict__[update_key] = values

    def add_basketball_item(self, stat_string: str):  # Run  Tested
        """
        adds a basketball stat string to the Team Stats object's attributes using __dict__
        stat is in format "Rebounds 45 62" -> self.rebonds = ["45", "62"]
        """
        basketball_keys = list(self.basketball_dict.keys())
        values = stat_string.split(' ')[-2:]
        matches = []
        for item in basketball_keys:
            if item in stat_string:
                if "Team Rebounds" not in stat_string:  # team rebounds always has 0's
                    matches.append(item)
        if len(matches) > 0:
            update_key = self.basketball_dict[max(matches, key=len)]
            self.__dict__[update_key] = values


class ESPN_Stat_Scraper:
    def __init__(self, league):
        self.league = league
        self.football_league = True if self.league in ["NFL", "NCAAF"] else False

    @property
    def link_dict(self):  # Property
        """
        Provides the prefix for each league's game sites on ESPN
        """
        link_dict = {
            "NFL": "https://www.espn.com/nfl/matchup?gameId=",
            "NBA": "https://www.espn.com/nba/matchup?gameId=",
            "NCAAF": "https://www.espn.com/college-football/matchup?gameId=",
            "NCAAB": "https://www.espn.com/mens-college-basketball/matchup?gameId="
        }
        return link_dict

    def get_stats_list(self, sp):  # Top Level
        """
        Scrapes the team stats highights from the sp/html

        these results are in a format like ['FG 24-63 22-47', 'Assists 6 11', ...]
        where the first part is the stat (FG), second is the away team's value (24-63), and
        third is the home team's value (22-47)
        """
        highlights = sp.find_all('tr', attrs={'class': 'highlight'})
        highlights += sp.find_all('tr', attrs={'class': 'indent'})
        results = []
        for item in highlights:
            item = item.get_text()
            item = item.replace('\t', '').replace('\n', ' ')
            for i in range(5):
                item = item.replace('  ', ' ')
            item = item.strip()
            results.append(item)
        return results

    def make_stats_object(self, stats_list):  # Top Level
        """
        uses the stats_list from get_stats_list to create a Team_Stats object for the game
        """
        ts = Team_Stats()
        for stat_string in stats_list:
            if self.football_league:
                ts.add_football_item(stat_string)
            else:
                ts.add_basketball_item(stat_string)
        return ts

    def run(self, espn_id):  # Run  Tested
        """
        Creates a Team_Stats object from an ESPN_ID
        """
        sp = get_sp1(self.link_dict[self.league] + str(espn_id))
        stats_list = self.get_stats_list(sp)
        team_stats = self.make_stats_object(stats_list)
        return team_stats

    def _has_team_stats(self, df):  # Specific Helper update_league_dfs
        """
        checks if a df has cols for team stats yet or not - if no, update_league_dfs will update it
        """
        df_cols = list(df.columns)
        return True if (("home_first_downs" in df_cols) or ("home_rebounds" in df_cols)) else False

    def update_df(self, df, path=None):  # Top Level upate_league_dfs
        """
        updates an entire df with team stats for each game - do not use to udpate a df with some team stats
        """
        ts = Team_Stats()
        cols = list(ts.football_dict.values()) if self.football_league else list(ts.basketball_dict.values())
        all_cols = ["home_" + col if i % 2 == 0 else "away_" + col for i,
                    col in enumerate([col for col in cols for i in range(2)])]

        for col in all_cols:
            df[col] = None

        for i, row in df.iterrows():
            print("{}/{}".format(i, len(df)))
            team_stats = self.run(row['ESPN_ID'])
            stats_row = team_stats.make_row(self.football_league)
            df.loc[i, all_cols] = stats_row
            time.sleep(5)

        if path is not None:
            df.to_csv(path, index=False)
        return df

    def update_league_dfs(self):  # Run
        """
        updates an entire league's dfs with team stats from scratch
        - this is used in the team folder structure before merging each team's data into one team csv
        """
        teams = os.listdir(ROOT_PATH + "/ESPN_Data/{}/".format(self.league))
        for team in teams:

            df_paths = os.listdir(ROOT_PATH + "/ESPN_Data/{}/{}/".format(self.league, team))
            df_paths = [path for path in df_paths if ((".csv" in path) and (int(path[-8:-4]) > 2007))]
            for path in df_paths:
                full_path = ROOT_PATH + "/ESPN_Data/{}/{}/".format(self.league, team) + path
                print(full_path)
                df = pd.read_csv(full_path)

                if not self._has_team_stats(df):
                    print(team, path[-8:-4])
                    try:
                        df = self.update_df(df, path=full_path)
                    except Exception as e:
                        print(e)
                        print("Error scraping team stats...")
                        time.sleep(30)

    def update_after_merge(self):  # Run
        """
        Updates team stats for all csv's in a league folder after they're merged to one df per team
        - This can be used to scrape missed team stats far in the past or right after a game finishes
        """
        all_cols = Team_Stats().all_cols(self.football_league)
        df_paths = listdir_fullpath(ROOT_PATH + "/ESPN_Data/{}/".format(self.league))
        null_col = "home_passing_yards" if self.football_league else "home_field_goals"

        for path in df_paths:
            print(path.split("/")[-1])
            df = pd.read_csv(path)
            df['datetime'] = pd.to_datetime(df['datetime']).apply(lambda x: x.date())
            for i, row in df.iterrows():
                if ((str(row[null_col]) == "nan") and (row['datetime'] < datetime.date.today())):
                    print("{}/{}  {} {} {}".format(i, len(df), row['Date'], row['Home'], row['Away']))
                    df.loc[i, all_cols] = self.run(str(int(row['ESPN_ID']))).make_row(self.football_league)
                    time.sleep(5)
            df.to_csv(path, index=False)


def parse_args(arg_list=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--league', help="HELP_MSG")
    parser.add_argument('--cmd', help="HELP_MSG")
    if arg_list is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arg_list)

    args_dict = vars(args)
    league = args_dict['league']
    cmd = args_dict['cmd']
    return league, cmd


if __name__ == "__main__":
    league, cmd = parse_args()
    x = ESPN_Stat_Scraper(league)
    self = x
    if cmd == "update":
        x.update_after_merge()
    else:
        x.update_league_dfs()
