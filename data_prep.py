# ==============================================================================
# File: data_prep.py
# Project: Sports_Betting
# File Created: Tuesday, 26th May 2020 2:55:40 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 26th May 2020 3:09:19 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# File for preparing data into ML-ready format
# ==============================================================================

import os
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Data_Prep:
    def __init__(self, league):
        self.league = league

    @property
    def team_folders(self):
        teams = os.listdir("./Data/{}".format(self.league))

    def get_all_dfs(self):
        team_paths = ["./Data/{}/{}".format(self.league, team)
                      for team in os.listdir("./Data/{}".format(self.league))]
        df_paths = []
        for team_path in team_paths:
            df_paths.append()
        return team_paths


if __name__ == "__main__":
    x = Data_Prep("NFL")
    team_paths = x.get_all_dfs()
