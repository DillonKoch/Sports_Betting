# ==============================================================================
# File: espn_clean_games.py
# Project: allison
# File Created: Tuesday, 17th August 2021 2:12:52 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 17th August 2021 2:13:02 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Cleaning ESPN games data to be ML-ready
# ==============================================================================


import json
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESPN_Clean_Games:
    def __init__(self, league):
        self.league = league
        self.copy_cols = ['Season', 'Week', 'Date', 'Network', 'Final_Status', 'H1H', 'H2H',
                          'H1Q', 'H2Q', 'H3Q', 'H4Q', 'HOT', 'A1H', 'A2H', 'A1Q', 'A2Q', 'A3Q', 'A4Q', 'AOT',
                          'Home_Final', 'Away_Final']

        self.copy_stats = ['1st_Downs', 'Passing_1st_downs', 'Rushing_1st_downs', '1st_downs_from_penalties',
                           'Total_Plays', 'Total_Yards', 'Total_Drives', 'Yards_per_Play', 'Passing',
                           'Yards_per_pass', 'Interceptions_thrown', 'Rushing', 'Rushing_Attempts',
                           'Yards_per_rush', 'Turnovers', 'Fumbles_lost', 'Defensive_Special_Teams_TDs']

        self.dash_stats = {"3rd_down_efficiency": ["3rd_downs_converted", "3rd_downs_total"],
                           "4th_down_efficiency": ["4th_downs_converted", "4th_downs_total"],
                           "Comp_Att": ["Passes_completed", "Passes_attempted"],
                           "Sacks_Yards_Lost": ["Sacks", "Sacks_Yards_Lost"],
                           "Red_Zone_Made_Att": ["Red_Zone_Conversions", "Red_Zone_Trips"],
                           "Penalties": ["Penalties", "Penalty_Yards"],
                           }
        self.time_stats = ['Possession']

    @property
    def team_dict(self):  # Property
        """
        dictionary of official team names
        """
        path = ROOT_PATH + f"/Data/Teams/{self.league}_Teams.json"
        with open(path) as f:
            team_dict = json.load(f)
        return team_dict

    def load_games_df(self):  # Top Level
        games_df = pd.read_csv(ROOT_PATH + f"/Data/ESPN/{self.league}/Games.csv")
        games_df = games_df.loc[games_df['Final_Status'].notnull()]
        return games_df

    def _official_name_dict(self):  # Specific Helper
        official_name_dict = {}
        for team in list(self.team_dict['Teams'].keys()):
            all_names = self.team_dict['Teams'][team]['Other Names'] + [team]
            for name in all_names:
                official_name_dict[name] = team

        for other_team in self.team_dict['Other Teams']:
            official_name_dict[other_team] = other_team

        return official_name_dict

    def add_home_away(self, new_df, games_df):  # Top Level
        official_name_dict = self._official_name_dict()
        new_df['Home'] = pd.Series([official_name_dict[name] for name in list(games_df['Home'])])
        new_df['Away'] = pd.Series([official_name_dict[name] for name in list(games_df['Away'])])
        return new_df

    def add_copy_stats(self, new_df, games_df):  # Top Level
        stat_names = []
        for stat in self.copy_stats:
            stat_names.append("Home_" + stat)
            stat_names.append("Away_" + stat)

        copy_stats_df = games_df[[col for col in stat_names]]
        new_df = pd.concat([new_df, copy_stats_df], axis=1)
        return new_df

    def _split_dash_vals(self, vals):  # Specific Helper  add_dash_stats
        dash1_vals = []
        dash2_vals = []
        for val in vals:
            if isinstance(val, float):
                dash1_vals.append(None)
                dash2_vals.append(None)
            else:
                d1_val, d2_val = val.split('-')
                dash1_vals.append(d1_val)
                dash2_vals.append(d2_val)
        return dash1_vals, dash2_vals

    def add_dash_stats(self, new_df, games_df):  # Top Level
        for dash_stat in list(self.dash_stats.keys()):
            for home_away in ['Home_', 'Away_']:
                vals = list(games_df[home_away + dash_stat])
                dash1_vals, dash2_vals = self._split_dash_vals(vals)
                new_df[self.dash_stats[dash_stat][0]] = pd.Series(dash1_vals)
                new_df[self.dash_stats[dash_stat][1]] = pd.Series(dash2_vals)
        return new_df

    def _poss_str_to_sec(self, poss_str):  # Specific Helper  add_time_stats
        """
        cleans a string of time like 10:43 into total seconds
        """
        if isinstance(poss_str, float) or (':' not in str(poss_str)):
            return None
        minutes, seconds = poss_str.split(':')
        total_seconds = (int(minutes) * 60) + int(seconds)
        return total_seconds

    def add_time_stats(self, new_df, games_df):  # Top Level
        """
        cleans the time-formatted stats like possession into total seconds, adds to new_df
        """
        for stat in self.time_stats:
            for home_away in ['Home_', 'Away_']:
                vals = list(games_df[home_away + stat])
                seconds = [self._poss_str_to_sec(val) for val in vals]
                new_df[home_away + stat] = pd.Series(seconds)

        return new_df

    def run(self):  # Run
        # clean names, clean fields so they're ML-ready
        # just copy over the columns that are already good to go
        # clean the other cols into newer cols
        games_df = self.load_games_df()

        new_df = games_df[[col for col in self.copy_cols if col in list(games_df.columns)]]
        new_df = self.add_home_away(new_df, games_df)
        new_df = self.add_copy_stats(new_df, games_df)
        new_df = self.add_dash_stats(new_df, games_df)
        new_df = self.add_time_stats(new_df, games_df)

        # TODO sort columns at the end
        new_df.to_csv(ROOT_PATH + f"/Data/ESPN/{self.league}.csv", index=False)
        return new_df


if __name__ == '__main__':
    league = "NCAAF"
    x = ESPN_Clean_Games(league)
    self = x
    new_df = x.run()
