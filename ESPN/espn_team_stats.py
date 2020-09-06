# ==============================================================================
# File: espn_team_stats.py
# Project: ESPN
# File Created: Saturday, 5th September 2020 2:27:02 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 5th September 2020 2:27:36 pm
# Modified By: Dillon Koch
# -----
#
# -----
# object to track team stats from ESPN
# ==============================================================================

from os.path import abspath, dirname
import sys

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


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
