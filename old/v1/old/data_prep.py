# ==============================================================================
# File: data_prep.py
# Project: Sports_Betting
# File Created: Tuesday, 26th May 2020 2:55:40 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 26th May 2020 4:07:40 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# File for preparing data into ML-ready format
# ==============================================================================

import copy
import os
import sys
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Data_Prep:
    def __init__(self, league):
        self.league = league

    def load_all_data(self):  # Top Level
        team_paths = ["./Data/{}/{}".format(self.league, team)
                      for team in os.listdir("./Data/{}".format(self.league))]
        df_paths = []
        for team_path in team_paths:
            df_paths += [team_path + '/' + item for item in os.listdir(team_path)]

        dfs = []
        for df_path in tqdm(df_paths):
            current_df = pd.read_csv(df_path)
            dfs.append(current_df)

        full_df = pd.concat(dfs)
        return full_df.drop_duplicates("ESPN_ID")

    def _replace_strings_in_col(self, old_df, col_name):  # Specific Helper remove_strings
        df = copy.deepcopy(old_df)
        col_values = list(df[col_name].value_counts().index)
        for val in col_values:
            if isinstance(val, str):
                df[col_name].replace(val, None, inplace=True)
        return df

    def remove_strings(self, df):  # Top Level
        pass

    def clean_overtimes(self, df):
        df.loc[df.HOT > 100, "HOT"] = None
        df.loc[df.AOT > 100, "AOT"] = None
        return df

    def run(self):  # Run
        df = self.load_all_data()
        # df = self.clean_overtimes(df)
        return df


if __name__ == "__main__":
    x = Data_Prep("NFL")
    df = x.run()
