# ==============================================================================
# File: team_stats_scraper.py
# Project: Season_Scrapers
# File Created: Tuesday, 16th June 2020 1:42:34 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 28th June 2020 4:51:59 pm
# Modified By: Dillon Koch
# -----
#
#
# -----
# Scraper to get the team stats for each game on ESPN
# ==============================================================================


import os
import sys
import time
import urllib.request
from os.path import abspath, dirname

import pandas as pd
from bs4 import BeautifulSoup as soup
from tqdm import tqdm


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.Utility import get_sp1


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

    def add_football_item(self, stat_string):  # Run
        football_keys = list(self.football_dict.keys())
        values = stat_string.split(' ')[-2:]
        matches = []
        for item in football_keys:
            if item in stat_string:
                matches.append(item)
        if len(matches) > 0:
            update_key = self.football_dict[max(matches, key=len)]
            self.__dict__[update_key] = values

    def add_basketball_item(self, stat_string):  # Run
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
    def link_dict(self):  # Global Helper
        link_dict = {
            "NFL": "https://www.espn.com/nfl/matchup?gameId=",
            "NBA": "https://www.espn.com/nba/matchup?gameId=",
            "NCAAF": "https://www.espn.com/college-football/matchup?gameId=",
            "NCAAB": "https://www.espn.com/mens-college-basketball/matchup?gameId="
        }
        return link_dict

    def get_tr_highlights(self, sp):  # Top Level
        highlights = sp.find_all('tr', attrs={'class': 'highlight'})
        results = []
        for item in highlights:
            item = item.get_text()
            item = item.replace('\t', '').replace('\n', ' ')
            for i in range(5):
                item = item.replace('  ', ' ')
            item = item.strip()
            results.append(item)
        return results

    def get_indents(self, sp):  # Top Level
        indents = sp.find_all('tr', attrs={'class': 'indent'})
        results = []
        for item in indents:
            item = item.get_text()
            item = item.replace('\t', '').replace('\n', ' ')
            for i in range(5):
                item = item.replace('  ', ' ')
            item = item.strip()
            results.append(item)
        return results

    def make_stats_object(self, stats_list):  # Top Level
        ts = Team_Stats()
        for stat_string in stats_list:
            if self.football_league:
                ts.add_football_item(stat_string)
            else:
                ts.add_basketball_item(stat_string)
        return ts

    def run(self, espn_id):  # Run
        sp = get_sp1(self.link_dict[self.league] + str(espn_id))
        tr_highlights = self.get_tr_highlights(sp)
        indents = self.get_indents(sp)
        stats_list = tr_highlights + indents
        team_stats = self.make_stats_object(stats_list)
        return team_stats

    def _has_team_stats(self, df):  # Specific Helper update_league_dfs
        df_cols = list(df.columns)
        return True if (("home_first_downs" in df_cols) or ("home_rebounds" in df_cols)) else False

    def _update_season_df(self, df):  # Specific Helper update_league_dfs
        ts = Team_Stats()
        cols = list(ts.football_dict.values()) if self.football_league else list(ts.basketball_dict.values())
        for col in cols:
            df["home_" + col] = None
            df["away_" + col] = None

        for i, row in df.iterrows():
            print("{}/{}".format(i, len(df)))
            team_stats = self.run(row['ESPN_ID'])
            stats_items = list(team_stats.__dict__.items())
            for col in cols:
                items = [tup[1] for tup in stats_items if tup[0] == col][0]
                if items is not None:
                    df.loc[i, "away_" + col] = items[0]
                    df.loc[i, "home_" + col] = items[1]
            time.sleep(5)

        df = df.loc[:, [item for item in list(df.columns) if "Unnamed" not in item]]
        return df

    def update_league_dfs(self):  # Run
        teams = os.listdir(ROOT_PATH + "/ESPN_Data/{}/".format(self.league))
        for team in teams:

            df_paths = os.listdir(ROOT_PATH + "/ESPN_Data/{}/{}/".format(self.league, team))
            df_paths = [path for path in df_paths if ((".csv" in path) and (int(path[-8:-4]) > 2007))]
            for path in df_paths:
                print(path)
                full_path = ROOT_PATH + "/ESPN_Data/{}/{}/".format(self.league, team) + path
                print(full_path)
                df = pd.read_csv(full_path)
                if not self._has_team_stats(df):
                    print(team, path[-8:-4])
                    try:
                        df = self._update_season_df(df)
                        df.to_csv(full_path, index=False)
                    except Exception as e:
                        print(e)
                        print("Error scraping team stats...")
                        time.sleep(30)


if __name__ == "__main__":
    x = ESPN_Stat_Scraper("NCAAF")
    self = x
    x.update_league_dfs()
    # espn_id = '401170371'
    # team_stats = x.run(espn_id)
