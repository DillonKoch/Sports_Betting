# ==============================================================================
# File: merge_league.py
# Project: ESPN_Scrapers
# File Created: Wednesday, 24th June 2020 4:50:25 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 24th June 2020 5:32:39 pm
# Modified By: Dillon Koch
# -----
#
# -----
# This file will merge each team's datasets into one csv per team
# Do this after adding all the team stats to each individual season df
# After this is done, new games will be added to each team's df and pulled to prod when done
# ==============================================================================

import os
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Merge_League:
    def __init__(self, league):
        self.league = league
        self.teams = os.listdir(ROOT_PATH + "/ESPN_Data/{}/".format(league))
        self.league_folder = ROOT_PATH + "/ESPN_Data/{}/".format(self.league)

    def run_one_team(self, team_name):
        csv_paths = [self.league_folder + "/{}/{}".format(team_name, item)
                     for item in os.listdir(self.league_folder + "/{}".format(team_name))]
        csv_paths = [item for item in csv_paths if int(item[-8:-4]) > 2007]
        dfs = [pd.read_csv(path) for path in csv_paths]
        full_df = pd.concat(dfs)
        full_df = full_df.loc[:, [col for col in list(full_df.columns) if "Unnamed" not in col]]
        full_df.sort_values(by="Season", inplace=True)
        new_csv_name = self.league_folder + team_name.replace(' ', '_') + '.csv'
        full_df.to_csv(new_csv_name, index=False)
        print("{} df created".format(team_name))

    def run_all_teams(self):
        for team in self.teams:
            self.run_one_team(team)
        print("DONE")


if __name__ == "__main__":
    x = Merge_League("NCAAF")
    # x.run_all_teams()
