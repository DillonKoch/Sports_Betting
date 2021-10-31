# ==============================================================================
# File: player_data.py
# Project: allison
# File Created: Sunday, 31st October 2021 2:55:59 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 31st October 2021 2:56:00 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Cleaning/combining player data to be fed into models
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Player_Data:
    def __init__(self, league):
        self.league = league

        # * player df with basic player info
        self.player_df = pd.read_csv(ROOT_PATH + f"/Data/ESPN/{self.league}/Players.csv")
        self.player_ids = [int(item) for item in list(self.player_df['Player_ID'])]

        # * stats df with player stats from each game
        self.stats_df = pd.read_csv(ROOT_PATH + f"/Data/ESPN/{self.league}/Stats.csv")

    def load_player_dict(self, player_id):  # Top Level
        """
        loading a dict of the player's basic info from Players.csv
        """
        if int(player_id) not in self.player_ids:
            raise ValueError(f"Player ID {player_id} not found in {self.league}/Players.csv")

        row = self.player_df.loc[self.player_df['Player_ID'] == int(player_id)]
        player_dict = dict(row.iloc[0])
        return player_dict

    def run(self, player_id, prev_games=10, use_avgs=True):  # Run
        # given a Player ID, return a list of the player's data
        # include: player info, stats
        # TODO madden ratings would eventually go here
        player_dict = self.load_player_dict(player_id)


if __name__ == '__main__':
    league = "NFL"
    player_id = "2330"
    x = Player_Data(league)
    self = x
    x.run(player_id)
