# ==============================================================================
# File: modeling_data.py
# Project: allison
# File Created: Saturday, 9th October 2021 8:07:03 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 9th October 2021 8:07:04 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Creating the final dataset to be used by ML algorithms
# ==============================================================================


import concurrent.futures
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def multithread(func, func_args):  # Multithreading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = list(tqdm(executor.map(func, func_args), total=len(func_args)))
    return result


class Modeling_Data:
    def __init__(self, league, num_past_games=10):
        self.league = league
        self.num_past_games = num_past_games

    def _clean_games_df(self, games_df):  # Specific Helper  load_game_dicts
        """
        cleaning up the games_df before it's broken up into dicts
        """
        # * filling overtime NaN's with 0
        games_df['HOT'].fillna(0, inplace=True)
        games_df['AOT'].fillna(0, inplace=True)
        return games_df

    def _games_feature_engineering(self, games_df):  # Specific Helper load_game_dicts
        """
        Engineering new target features to be modeled
        """
        # * Home_Win
        games_df['Home_Win'] = games_df['Home_Final'] > games_df['Away_Final']
        games_df['Home_Win'] = games_df['Home_Win'].astype(int)
        # * Home_Win_Margin
        games_df['Home_Win_Margin'] = games_df['Home_Final'] - games_df['Away_Final']
        # * Home_Covered
        games_df['Home_Covered'] = (games_df['Home_Final'] + games_df['Home_Line_Close']) > games_df['Away_Final']
        games_df['Home_Covered'] = games_df['Home_Covered'].astype(int)
        # * Over_Covered
        games_df['Over_Covered'] = (games_df['Home_Final'] + games_df['Away_Final']) > games_df['OU_Close']
        games_df['Over_Covered'] = games_df['Over_Covered'].astype(int)
        return games_df

    def load_game_dicts(self):  # Top Level
        """
        loads all the games (rows) from /Data/{league}.csv into a list of dicts for each game
        """
        games_df = pd.read_csv(ROOT_PATH + f"/Data/{self.league}.csv")
        games_df = self._clean_games_df(games_df)
        games_df = self._games_feature_engineering(games_df)
        game_dicts = [{col: val for col, val in zip(list(games_df.columns), df_row)} for df_row in games_df.values.tolist()]
        return game_dicts

    def _quarters_halves_final(self):  # Specific Helper get_feature_cols
        """
        making a list of quarters/halves depending on the league, and finals/overtimes
        """
        overtimes = ['HOT', 'AOT']
        finals = ['Home_Final', 'Away_Final']
        halves = ['H1H', 'H2H', 'A1H', 'A2H'] + overtimes + finals
        quarters = ['H1Q', 'H2Q', 'H3Q', 'H4Q', 'A1Q', 'A2Q', 'A3Q', 'A4Q'] + overtimes + finals
        return halves if self.league == "NCAAB" else quarters

    def _game_stats(self):  # Specific Helper get_feature_cols
        """
        returning a list of team stats for the given league
        """
        nfl_stats = ['Home_1st_Downs', 'Away_1st_Downs']
        ncaaf_stats = []
        nba_stats = []
        ncaab_stats = []
        stat_dict = {"NFL": nfl_stats, "NBA": nba_stats, "NCAAF": ncaaf_stats, "NCAAB": ncaab_stats}
        return stat_dict[self.league]

    def get_feature_cols(self):  # Top Level
        """
        making a list of all the feature_cols to be put in the df
        """
        feature_cols = []
        feature_cols += self._quarters_halves_final()
        feature_cols += self._game_stats()
        return feature_cols

    def _team_eligible_index(self, game_dicts, team):  # Specific Helper get_eligible_game_dicts
        """
        finds the index in game_dicts in which the team has enough data for modeling
        """
        count = 0
        for i, game_dict in enumerate(game_dicts):
            home = game_dict['Home']
            away = game_dict['Away']
            if team in [home, away]:
                count += 1
            if count == self.num_past_games:
                return i
        return np.Inf

    def get_eligible_game_dicts(self, game_dicts):  # Top Level
        """
        Building a list of "eligible" game_dicts in which both teams have enough past data for modeling
        """
        # * making a list of teams and the index in game_dicts in which that team has enough data for modeling
        teams = list(set([gd['Home'] for gd in game_dicts] + [gd['Away'] for gd in game_dicts]))
        team_eligible_indices = {team: self._team_eligible_index(game_dicts, team) for team in teams}

        # * looping through game_dicts to create eligible_game_dicts, with only games where teams have enough data
        eligible_game_dicts = []
        for i, team_dict in enumerate(game_dicts):
            home_eligible = i > team_eligible_indices[team_dict['Home']]
            away_eligible = i > team_eligible_indices[team_dict['Away']]
            if (home_eligible and away_eligible):
                eligible_game_dicts.append(team_dict)

        # * eligible_game_dicts are sorted from oldest-newest
        eligible_game_dicts = sorted(eligible_game_dicts, key=lambda x: x['Date'])
        return eligible_game_dicts

    def _game_dicts_before_date(self, game_dicts, date):  # Specific Helper query_recent_games
        prev_game_dicts = []
        for game_dict in game_dicts:
            if game_dict["Date"] < date:
                prev_game_dicts.append(game_dict)
            else:
                break
        # * reversing so query_recent_games() stops after finding the most recent games
        prev_game_dicts.reverse()
        return prev_game_dicts

    def query_recent_games(self, team, date, game_dicts):  # Top Level
        """
        loops through prev_game_dicts to find the most recent 'self.num_past_games' games involving 'team'
        """
        prev_game_dicts = self._game_dicts_before_date(game_dicts, date)
        recent_games = []
        for prev_game_dict in prev_game_dicts:
            home = prev_game_dict['Home']
            away = prev_game_dict['Away']
            if team in [home, away]:
                recent_games.append(prev_game_dict)
            if len(recent_games) == self.num_past_games:
                return recent_games
        raise ValueError("Didn't find enough recent games!")

    def _get_opp_feature_col(self, feature_col, home_feature):  # Specific Helper avg_feature_col
        opp_feature_col = feature_col.replace("Home", "Away") if home_feature else feature_col.replace("Away", "Home")
        opp_feature_col = 'A' + opp_feature_col[1:] if home_feature else 'H' + opp_feature_col[1:]
        return opp_feature_col

    def avg_feature_col(self, feature_col, home, away, home_recent_games, away_recent_games):  # Top Level
        """
        Computing the average value of 'feature_col' in recent games
        - inspects home/away recent games based on name of feature_col
        """
        home_feature = True if feature_col[0] == 'H' else False
        recent_games = home_recent_games if home_feature else away_recent_games
        team = home if home_feature else away

        opp_feature_col = self._get_opp_feature_col(feature_col, home_feature)
        home_feature_col = feature_col if home_feature else opp_feature_col
        away_feature_col = opp_feature_col if home_feature else feature_col
        vals = []
        for recent_game_dict in recent_games:
            team_is_home = True if recent_game_dict['Home'] == team else False
            new_val = recent_game_dict[home_feature_col] if team_is_home else recent_game_dict[away_feature_col]
            vals.append(new_val)

        return round(sum(vals) / len(vals), 2)

    def add_targets(self, targets, game_dict, new_row_dict):  # Top Level
        """
        adding specified targets to the final df straight from the merged df
        """
        for target in targets:
            new_row_dict[target] = game_dict[target]
        return new_row_dict

    def build_new_row_dict(self, args):  # Top Level
        """
        Given the home/away team and game date, this will create a new_row_dict for ML training
        """
        home, away, date, feature_cols, eligible_game_dict, game_dicts = args
        home_recent_games = self.query_recent_games(home, date, game_dicts)
        away_recent_games = self.query_recent_games(away, date, game_dicts)

        new_row_dict = {feature_col: self.avg_feature_col(feature_col, home, away, home_recent_games, away_recent_games)
                        for feature_col in feature_cols}
        new_row_dict = self.add_targets(targets, eligible_game_dict, new_row_dict)
        return new_row_dict

    def run(self, targets):  # Run
        # * game dicts, feature_cols, eligible
        game_dicts = self.load_game_dicts()
        feature_cols = self.get_feature_cols()  # ! all feature cols can be queried numerically!
        eligible_game_dicts = self.get_eligible_game_dicts(game_dicts)

        # * multithreading the process of creating a new row for the df based on every eligible_game_dict
        args = [(egd['Home'], egd['Away'], egd['Date'], feature_cols, egd, game_dicts) for egd in eligible_game_dicts]
        new_row_dicts = multithread(self.build_new_row_dict, args)

        df = pd.DataFrame(new_row_dicts, columns=feature_cols + targets)

        return df

    def future_game_to_new_row_dict(self, targets):  # Run
        game_dicts = self.load_game_dicts()
        # TODO assert that there's enough data for the two teams
        # TODO run build_new_row_dict with input info


if __name__ == '__main__':
    league = "NFL"
    targets = ['Home_ML', 'Home_Win', 'Home_Win_Margin', 'Home_Covered', 'Over_Covered']
    x = Modeling_Data(league)
    self = x
    df = x.run(targets)
