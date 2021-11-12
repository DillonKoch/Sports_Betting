# ==============================================================================
# File: clean_espn.py
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
import warnings
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

warnings.filterwarnings("ignore")


class Clean_ESPN:
    def __init__(self, league):
        self.league = league
        self.football_league = league in ['NFL', 'NCAAF']

        self.copy_cols = ['Season', 'Week', 'Date', 'Network', 'Final_Status', 'H1H', 'H2H',
                          'H1Q', 'H2Q', 'H3Q', 'H4Q', 'HOT', 'A1H', 'A2H', 'A1Q', 'A2Q', 'A3Q', 'A4Q', 'AOT',
                          'Home_Final', 'Away_Final']

        # ! Stats being copied over to new dataframe
        self.football_copy_stats = ['1st_Downs', 'Passing_1st_downs', 'Rushing_1st_downs', '1st_downs_from_penalties',
                                    'Total_Plays', 'Total_Yards', 'Total_Drives', 'Yards_per_Play', 'Passing',
                                    'Yards_per_pass', 'Interceptions_thrown', 'Rushing', 'Rushing_Attempts',
                                    'Yards_per_rush', 'Turnovers', 'Fumbles_lost', 'Defensive_Special_Teams_TDs']
        self.basketball_copy_stats = ['Field_Goal_pct', 'Three_Point_pct', 'Free_Throw_pct', 'Rebounds',
                                      'Offensive_Rebounds', 'Defensive_Rebounds', 'Assists', 'Steals', 'Blocks',
                                      'Total_Turnovers', 'Points_Off_Turnovers', 'Fast_Break_Points',
                                      'Points_in_Paint', 'Fouls', 'Technical_Fouls', 'Flagrant_Fouls',
                                      'Largest_Lead']
        self.copy_stats = self.football_copy_stats if self.football_league else self.basketball_copy_stats

        # ! Stats with dashes that require cleaning for new dataframe
        self.football_dash_stats = {"3rd_down_efficiency": ["3rd_downs_converted", "3rd_downs_total"],
                                    "4th_down_efficiency": ["4th_downs_converted", "4th_downs_total"],
                                    "Comp_Att": ["Passes_completed", "Passes_attempted"],
                                    "Sacks_Yards_Lost": ["Sacks", "Sacks_Yards_Lost"],
                                    "Red_Zone_Made_Att": ["Red_Zone_Conversions", "Red_Zone_Trips"],
                                    "Penalties": ["Penalties", "Penalty_Yards"],
                                    }
        self.basketball_dash_stats = {"FG": ["FG_made", "FG_attempted"],
                                      "3PT": ["3PT_made", "3PT_attempted"],
                                      "FT": ["FT_made", "FT_attempted"]}
        self.dash_stats = self.football_dash_stats if self.football_league else self.basketball_dash_stats

        self.time_stats = ['Possession'] if self.football_league else []

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
        """
        loading the league's games.csv dataframe from /Data/ESPN/{league}
        - removing unfinished games
        """
        games_df = pd.read_csv(ROOT_PATH + f"/Data/ESPN/{self.league}/Games.csv")
        # games_df = games_df.loc[games_df['Final_Status'].notnull()]
        games_df = games_df.loc[games_df['Home'].notnull()]
        games_df.reset_index(inplace=True)
        return games_df

    def _official_name_dict(self):  # Specific Helper  add_home_away
        """
        Reversing the dict in Teams.json so any of the known names for a team maps to the official name
        """
        official_name_dict = {}
        for team in list(self.team_dict['Teams'].keys()):
            all_names = self.team_dict['Teams'][team]['Other Names'] + [team]
            for name in all_names:
                official_name_dict[name] = team

        for other_team in self.team_dict['Other Teams']:
            official_name_dict[other_team] = other_team

        return official_name_dict

    def add_home_away(self, new_df, games_df):  # Top Level
        """
        Adding official Home/Away team names from the Teams.json file in /Data/Teams/
        """
        official_name_dict = self._official_name_dict()
        new_df['Home'] = pd.Series([official_name_dict[name] for name in list(games_df['Home'])])
        new_df['Away'] = pd.Series([official_name_dict[name] for name in list(games_df['Away'])])
        return new_df

    def add_copy_stats(self, new_df, games_df):  # Top Level
        """
        Moving over stats from games_df to new_df that don't require any cleaning
        """
        stat_names = []
        for stat in self.copy_stats:
            stat_names.append("Home_" + stat)
            stat_names.append("Away_" + stat)

        copy_stats_df = games_df[[col for col in stat_names]]
        new_df = pd.concat([new_df, copy_stats_df], axis=1)
        return new_df

    def _split_dash_vals(self, vals):  # Specific Helper  add_dash_stats
        """
        Extracting the first/second parts of the dash stat
        """
        dash1_vals = []
        dash2_vals = []
        for val in vals:
            if isinstance(val, float) or val in ['--']:
                dash1_vals.append(None)
                dash2_vals.append(None)
            else:
                d1_val, d2_val = val.split('-')
                dash1_vals.append(d1_val)
                dash2_vals.append(d2_val)
        return dash1_vals, dash2_vals

    def add_dash_stats(self, new_df, games_df):  # Top Level
        """
        Adding stats with dashes (like Penalties-Yards) to the new_df
        """
        for dash_stat in list(self.dash_stats.keys()):
            for home_away in ['Home_', 'Away_']:
                vals = list(games_df[home_away + dash_stat])
                dash1_vals, dash2_vals = self._split_dash_vals(vals)
                new_df[home_away + self.dash_stats[dash_stat][0]] = pd.Series(dash1_vals)
                new_df[home_away + self.dash_stats[dash_stat][1]] = pd.Series(dash2_vals)
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
        games_df = self.load_games_df()

        new_df = games_df[[col for col in self.copy_cols if col in list(games_df.columns)]]
        new_df = self.add_home_away(new_df, games_df)
        new_df = self.add_copy_stats(new_df, games_df)
        new_df = self.add_dash_stats(new_df, games_df)
        new_df = self.add_time_stats(new_df, games_df)

        new_df = new_df.sort_values(by=['Date'])
        new_df.to_csv(ROOT_PATH + f"/Data/ESPN/{self.league}.csv", index=False)
        return new_df


if __name__ == '__main__':

    # running all
    for league in tqdm(['NFL', 'NBA', 'NCAAF', 'NCAAB']):
        # for league in ['NCAAB']:
        x = Clean_ESPN(league)
        self = x
        new_df = x.run()
