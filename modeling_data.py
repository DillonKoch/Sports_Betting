# ==============================================================================
# File: modeling_data.py
# Project: allison
# File Created: Friday, 10th September 2021 2:07:57 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 10th September 2021 2:07:58 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Creating data useful for modeling
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Modeling_Data:
    def __init__(self, league):
        self.league = league
        self.game_info_cols = []

        # * loading the league's data from /Data, putting games into a list of dictionaries
        self.games_df = pd.read_csv(ROOT_PATH + f"/Data/{self.league}.csv")
        self.game_dicts = [{col: val for col, val in zip(list(self.games_df.columns), df_row)} for df_row in self.games_df.values.tolist()]
        self.game_dicts.reverse()

    def blank_data(self, features, num_games, avg):  # Top Level
        """
        creating a blank dataset to populate with ML-ready data
        - columns differ based on num_games and whether we're taking avg or not
        """
        if avg:
            home = ['Home_' + feature + '_avg' for feature in features]
            away = ['Away_' + feature + '_avg' for feature in features]
            cols = [home + away + self.game_info_cols]
        else:
            home = ['Home_' + feature + f'_{i}' for feature in features for i in range(num_games)]
            away = ['Away_' + feature + f'_{i}' for feature in features for i in range(num_games)]
            cols = [home + away + self.game_info_cols]
        return pd.DataFrame(columns=cols)

    def _prev_game_dicts(self, game_dicts, team, num_games):  # Specific Helper query_team_stats
        """
        given all the remanining game dicts, this will find the next num_games games
        that include the team of interest
        """
        prev_games = []
        for game_dict in game_dicts:
            if team in [game_dict['Home'], game_dict['Away']]:
                prev_games.append(game_dict)

            if len(prev_games) == num_games:
                return prev_games
        return prev_games

    def query_team_stats(self, game_dicts, features, team, num_games, avg):  # Top Level
        """
        given game_dicts and a team, this will grab the raw/avg team stats for the last num_games
        """
        # * populating the stat_dict with raw stats from the last num_games
        stat_dict = {feature: [] for feature in features}
        prev_game_dicts = self._prev_game_dicts(game_dicts, team, num_games)
        for prev_game_dict in prev_game_dicts:
            team_is_home = prev_game_dict['Home'] == team
            for feature in features:
                home_away_feature = 'Home_' + feature if team_is_home else 'Away_' + feature
                stat = prev_game_dict[home_away_feature]
                stat_dict[feature].append(stat)

        # * changing the stat_dict to the avg value instead of list of raw values, if necessary
        if avg:
            stat_dict = {feature: (sum(stat_dict[feature]) / len(stat_dict[feature])) for feature in features}

        return stat_dict

    def game_info(self, game_dict):  # Top Level
        """
        just getting basic info about the game like day, time, network - stuff available before games
        """
        return []

    def new_game_row(self, data_cols, features, home_stats, away_stats, avg):  # Top Level
        """
        converting home/away stats, game info leading up to a game into a list that will go into the data df
        - if taking average, home/away stats contain the average value
        - if not taking average, home/away stats have a list of the raw values
        - data_cols has one _avg col per feature if taking avg, else _i cols for each raw value
        """
        row = []
        if avg:
            for home_away_stats in [home_stats, away_stats]:
                for feature in features:
                    row.append(home_away_stats[feature])

        else:
            for home_away_stats in [home_stats, away_stats]:
                for feature in features:
                    row += home_away_stats[feature]

        return row

    def get_targets(self, targets):  # Top Level
        """
        creating a dataframe of the target values for all games in self.game_dicts
        """
        targets = pd.DataFrame(columns=targets)
        for game_dict in self.game_dicts[:1000]:
            new_targets = [game_dict[target] for target in targets]
            targets.loc[len(targets)] = new_targets
        return targets

    def scale_data(self, data):  # Top Level
        scaler = StandardScaler()
        data = scaler.fit_transform(data)
        return data, scaler

    def run(self, features, targets, num_games=5, avg=False):  # Run
        # TODO handle categorical variables
        # TODO generate targets like Home_Win
        # TODO implement game info
        # * creating blank dataframe
        data = self.blank_data(features, num_games, avg)
        data_cols = list(data.columns)

        # * looping over every game in the data, adding raw/avg values to dataframe
        for i, game_dict in tqdm(enumerate(self.game_dicts[:1000])):
            home = game_dict['Home']
            away = game_dict['Away']

            # * querying stats from recent n games, current game info
            home_stats = self.query_team_stats(self.game_dicts[i + 1:], features, home, num_games, avg)
            away_stats = self.query_team_stats(self.game_dicts[i + 1:], features, away, num_games, avg)
            # game_info = self.game_info(game_dict)

            # * combining data and adding to row of 'data'
            new_row = self.new_game_row(data_cols, features, home_stats, away_stats, avg)
            data.loc[len(data)] = new_row

        # * grabbing target data from df
        target_data = self.get_targets(targets)

        # model takes in [team_1_stats, team_2_stats] => predicts => [target(s)]
        data, scaler_x = self.scale_data(data)
        target_data, scaler_y = self.scale_data(target_data)

        X_train, X_test, y_train, y_test = train_test_split(data, target_data, test_size=0.2, random_state=18)
        return X_train, X_test, y_train, y_test, scaler_y


if __name__ == '__main__':
    x = Modeling_Data("NFL")
    self = x
    game_dicts = x.game_dicts
    features = ['1st_Downs']
    targets = ['Home_ML']
    num_games = 5
    avg = False
    team = 'Minnesota Vikings'
    X_train, X_test, y_train, y_test, scaler_y = x.run(features, targets)
