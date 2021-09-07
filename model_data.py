# ==============================================================================
# File: model_data.py
# Project: allison
# File Created: Tuesday, 17th August 2021 1:35:59 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 17th August 2021 1:36:01 pm
# Modified By: Dillon Koch
# -----
#
# -----
# preparing modeling data for any ML modeline
# ==============================================================================


import sys
from itertools import chain
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Model_Data:
    def __init__(self, league):
        self.league = league

        # self.espn_df = pd.read_csv(ROOT_PATH + f"/Data/ESPN/{self.league}.csv")
        # self.espn_cols = list(self.espn_df.columns) + ['Home_Win']

        # self.odds_df = pd.read_csv(ROOT_PATH + f"/Data/Odds/{self.league}.csv")
        # self.odds_cols = list(self.odds_df.columns)

        # self.esb_df = None
        # self.esb_cols = []

        # self.data = pd.merge(self.espn_df, self.odds_df)
        self.games_df = pd.read_csv(ROOT_PATH + f"/Data/{self.league}.csv")
        self.game_dicts = [{col: val for col, val in zip(list(self.games_df.columns), df_row)} for df_row in self.games_df.values.tolist()]
        self.game_dicts.reverse()

    def query_games(self, team, date, num_past_games):  # Top Level
        games = []
        for game_dict in self.game_dicts:
            if (game_dict['Date'] < date) and (team in [game_dict['Home'], game_dict['Away']]):
                games.append(game_dict)
                if len(games) == num_past_games:
                    return games
        return None

    def stat_metric(self, team, games, feature, metric):  # Top Level
        vals = []
        for game in games:
            team_is_home = game['Home'] == team
            col_name = feature if team_is_home else feature.replace("Home_", "Away_")
            new_val = game[col_name]
            vals.append(new_val)
        if metric == 'vals':
            return vals
        elif metric == 'mean':
            return sum(vals) / len(vals)

    def target_game(self, home, away, date):  # Top Level
        for game in self.game_dicts:
            if (game['Home'] == home) and (game['Away'] == away) and (game['Date'] == date):
                return game
        raise ValueError(f"{home} vs {away} on {date} NOT FOUND")

    def game_to_model_data(self, home, away, date, features, targets, past_games=5):  # Run
        """
        set targets=None to just return input data (for running model in PROD)
        """
        home_games = self.query_games(home, date, past_games)
        away_games = self.query_games(away, date, past_games)
        if (home_games is None) or (away_games is None):
            print(f"Not enough data for {past_games} games before {date} for {home} vs {away}")
            return None

        model_data = {}
        for feature in features:
            home_metric = self.stat_metric(home, home_games, feature, metric='mean')
            model_data[feature] = home_metric
            away_metric = self.stat_metric(away, away_games, feature, metric='mean')
            model_data[feature] = away_metric

        # ! CANNOT TAKE AVERAGE OF TARGETS!!
        if targets is not None:
            target_game = self.target_game(home, away, date)
            for target in targets:
                model_data[target] = target_game[target]
                model_data[target] = target_game[target]
        return model_data

    def training_data(self, features, targets, past_games=5):  # Run
        data = pd.DataFrame(columns=features + targets)
        for game_dict in tqdm(self.game_dicts):
            home = game_dict['Home']
            away = game_dict['Away']
            date = game_dict['Date']
            # ! right here - just have a method for getting a certain team's stats
            # ! forget about home/away, go grab their last 5 game avg, put into array, return
            model_data_dict = self.game_to_model_data(home, away, date, features, targets, past_games)
            if model_data_dict is not None:
                data.loc[len(data)] = model_data_dict
        return data.dropna()


if __name__ == '__main__':
    league = "NFL"
    x = Model_Data(league)
    self = x

    home = "Tampa Bay Buccaneers"
    away = "Kansas City Chiefs"
    date = '2021-02-07'
    features = ['Home_1st_Downs', 'Home_Passing_1st_downs', 'H1Q', 'A4Q']
    targets = ['Home_Final']
    model_data = x.game_to_model_data(home, away, date, features, targets, past_games=100)
    data = x.training_data(features, targets)
