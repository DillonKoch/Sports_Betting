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

from Data_Cleaning.player_data import Player_Data


def multithread(func, func_args):  # Multithreading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = list(tqdm(executor.map(func, func_args), total=len(func_args)))
    return result


class Modeling_Data:
    def __init__(self, league, num_past_games=10):
        self.league = league
        self.num_past_games = num_past_games
        self.player_data = Player_Data(league)
        self.betting_cols = ['Home_Line_Close', 'Home_Line_Close_ML', 'OU_Close', 'OU_Close_ML',
                             'Home_ML', 'Away_ML']
        self.targets = ['Home_Covered', 'Home_Win', 'Over_Covered']

    def _filter_dates(self, games_df, start_date, end_date):  # Specific Helper load_game_data
        """
        filters the game_df down to games within the date range
        """
        pass

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
        Engineering new target features to be modeled for each bet type
        """
        # ? TODO keep everything None for unplayed games
        # * Spread - Home_Covered
        games_df['Home_Covered'] = (games_df['Home_Final'] + games_df['Home_Line_Close']) > games_df['Away_Final']
        games_df['Home_Covered'] = games_df['Home_Covered'].astype(int)
        # * MoneyLine - Home_Win
        games_df['Home_Win'] = games_df['Home_Final'] > games_df['Away_Final']
        games_df['Home_Win'] = games_df['Home_Win'].astype(int)
        # * Total: Over_Covered
        games_df['Over_Covered'] = (games_df['Home_Final'] + games_df['Away_Final']) > games_df['OU_Close']
        games_df['Over_Covered'] = games_df['Over_Covered'].astype(int)

        for col in ['Home_Win', 'Home_Covered', 'Over_Covered']:
            games_df.loc[games_df['Final_Status'].isnull(), col] = None
        return games_df

    def load_game_dicts(self):  # Top Level
        """
        loads all the games (rows) from /Data/{league}.csv into a list of dicts for each game
        """
        games_df = pd.read_csv(ROOT_PATH + f"/Data/{self.league}.csv")
        # games_df = self.filter_dates(games_df)
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

    def _wrap_home_away(self, stat_list):  # Helping Helper _game_stats
        home = ['Home_' + stat for stat in stat_list]
        away = ['Away_' + stat for stat in stat_list]
        return home + away

    def _game_stats(self):  # Specific Helper get_feature_cols
        """
        returning a list of team stats for the given league
        """
        nfl_stats = ['1st_Downs', 'Passing_1st_downs', 'Rushing_1st_downs', '1st_downs_from_penalties',
                     'Total_Plays', 'Total_Yards', 'Total_Drives', 'Yards_per_Play', 'Passing',
                     'Yards_per_pass', 'Interceptions_thrown', 'Rushing', 'Rushing_Attempts',
                     'Yards_per_rush', 'Turnovers', 'Fumbles_lost', 'Defensive_Special_Teams_TDs',
                     '3rd_downs_converted', '3rd_downs_total', '4th_downs_converted', '4th_downs_total',
                     'Passes_completed', 'Passes_attempted', 'Sacks', 'Sacks_Yards_Lost',
                     'Red_Zone_Conversions', 'Red_Zone_Trips', 'Penalties', 'Penalty_Yards', 'Possession']
        ncaaf_stats = ['1st_Downs',
                       'Total_Yards', 'Passing', 'Yards_per_pass', 'Interceptions_thrown', 'Rushing',
                       'Rushing_Attempts', 'Yards_per_rush', 'Turnovers', 'Fumbles_lost',
                       '3rd_downs_converted', '3rd_downs_total', '4th_downs_converted', '4th_downs_total',
                       'Passes_completed', 'Passes_attempted', 'Penalties', 'Penalty_Yards', 'Possession']
        nba_stats = ['Field_Goal_pct', 'Three_Point_pct', 'Free_Throw_pct', 'Rebounds', 'Offensive_Rebounds',
                     'Defensive_Rebounds', 'Assists', 'Steals', 'Blocks', 'Total_Turnovers', 'Points_Off_Turnovers',
                     'Fast_Break_Points', 'Points_in_Paint', 'Fouls', 'Technical_Fouls', 'Flagrant_Fouls',
                     'Largest_Lead', 'FG_made', 'FG_attempted', '3PT_made', '3PT_attempted', 'FT_made',
                     'FT_attempted']
        ncaab_stats = ['Field_Goal_pct', 'Three_Point_pct', 'Free_Throw_pct', 'Rebounds', 'Offensive_Rebounds',
                       'Defensive_Rebounds', 'Assists', 'Steals', 'Blocks', 'Total_Turnovers', 'Fouls',
                       'Technical_Fouls', 'Flagrant_Fouls', 'Largest_Lead', 'FG_made', 'FG_attempted',
                       '3PT_made', '3PT_attempted', 'FT_made', 'FT_attempted']
        stat_dict = {"NFL": self._wrap_home_away(nfl_stats), "NBA": self._wrap_home_away(nba_stats),
                     "NCAAF": self._wrap_home_away(ncaaf_stats), "NCAAB": self._wrap_home_away(ncaab_stats)}
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
            if 'Final' not in str(prev_game_dict['Final_Status']):
                continue

            home = prev_game_dict['Home']
            away = prev_game_dict['Away']
            if team in [home, away]:
                recent_games.append(prev_game_dict)
            if len(recent_games) == self.num_past_games:
                return recent_games
        raise ValueError("Didn't find enough recent games!")

    def _get_opp_feature_col(self, feature_col, home_feature):  # Helping Helper _avg_feature_col
        opp_feature_col = feature_col.replace("Home", "Away") if home_feature else feature_col.replace("Away", "Home")
        opp_feature_col = 'A' + opp_feature_col[1:] if home_feature else 'H' + opp_feature_col[1:]
        return opp_feature_col

    def _avg_feature_col(self, feature_col, home, away, home_recent_games, away_recent_games):  # Specific Helper build_new_row_dict
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

    def _add_targets_bet_cols(self, game_dict, new_row_dict):  # Specific Helper build_new_row_dict
        """
        adding targets and betting columns to the final df straight from the merged df
        - these are not averaged across past games like the other features
        """
        for target in self.targets + self.betting_cols:
            new_row_dict[target] = game_dict[target]
        return new_row_dict

    def build_new_row_dict(self, args):  # Top Level
        """
        Given the home/away team and game date, this will create a new_row_dict for ML training
        """
        home, away, date, feature_cols, eligible_game_dict, game_dicts = args
        home_recent_games = self.query_recent_games(home, date, game_dicts)
        away_recent_games = self.query_recent_games(away, date, game_dicts)

        # TODO RIGHT HERE IS WHERE I NEED TO INCORPORATE STAT_ALLOWED, FOR EACH TEAM, NOT JUST WHAT THE ONE TEAM PRODUCED
        new_row_dict = {feature_col: self._avg_feature_col(feature_col, home, away, home_recent_games, away_recent_games)
                        for feature_col in feature_cols}

        new_row_dict = self._add_targets_bet_cols(eligible_game_dict, new_row_dict)
        return new_row_dict

    def fill_na_values(self, df, feature_cols):  # Top Level
        """
        simple mean-imputation for missing values in feature columns
        """
        for feature_col in feature_cols:
            df[feature_col].fillna(value=df[feature_col].mean(), inplace=True)
        return df

    def add_player_stats(self, eligible_game_dicts, df):  # Top Level
        """
        Adding player stats to the df
        """
        home_teams = [egd['Home'] for egd in eligible_game_dicts]
        away_teams = [egd['Away'] for egd in eligible_game_dicts]
        dates = [egd['Date'] for egd in eligible_game_dicts]

        new_df_cols = ["H" + item for item in self.player_data.feature_col_names] + ['A' + item for item in self.player_data.feature_col_names]
        new_df = pd.DataFrame(columns=new_df_cols)

        def run_player_data(args):
            team, date = args
            return self.player_data.run(team, date)

        home_inputs = [(home_team, date) for home_team, date in zip(home_teams, dates)]
        home_stats = multithread(run_player_data, home_inputs)
        away_inputs = [(away_team, date) for away_team, date in zip(away_teams, dates)]
        away_stats = multithread(run_player_data, away_inputs)

        for i, (home_stat, away_stat) in enumerate(zip(home_stats, away_stats)):
            new_df.loc[len(new_df)] = home_stat + away_stat

        # final_df = pd.merge(df, new_df, how='left', on=['Home', 'Away', 'Date'])
        final_df = pd.concat([df, new_df], axis=1)
        return final_df

    def run(self, player_stats=True):  # Run
        # * game dicts, feature_cols, eligible
        game_dicts = self.load_game_dicts()
        feature_cols = self.get_feature_cols()
        eligible_game_dicts = self.get_eligible_game_dicts(game_dicts)

        # * multithreading the process of creating a new row for the df based on every eligible_game_dict
        args = [(egd['Home'], egd['Away'], egd['Date'], feature_cols, egd, game_dicts) for egd in eligible_game_dicts]
        new_row_dicts = multithread(self.build_new_row_dict, args)

        df = pd.DataFrame(new_row_dicts, columns=self.betting_cols + self.targets + feature_cols)
        df = self.fill_na_values(df, feature_cols)
        if player_stats:
            df = self.add_player_stats(eligible_game_dicts, df)

        return df

    def run_all(self):  # Run
        """
        running this file to create datasets with/without player stats for all leagues
        - saving to /Modeling
        - "pg" = past games, "nps" = no player stats, "wps" = with player stats
        """
        df_no_p_stats = self.run(player_stats=False)
        df_no_p_stats.to_csv(f"{ROOT_PATH}/Data/Modeling_Data/{self.league}/no_player_stats_avg_{self.past_games_num}_past_games.csv", index=False)
        df_p_stats = self.run(player_stats=True)
        df_p_stats.to_csv(f"{ROOT_PATH}/Modeling/{league}/player_stats_avg_{self.past_games_num}_past_games.csv", index=False)


if __name__ == '__main__':
    # for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
    for league in ['NBA']:
        x = Modeling_Data(league)
        x.run_all()
