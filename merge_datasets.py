# ==============================================================================
# File: merge_datasets.py
# Project: allison
# File Created: Monday, 16th August 2021 4:13:20 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 16th August 2021 4:13:21 pm
# Modified By: Dillon Koch
# -----
#
# -----
# merging various datasets on Date, Home/Away teams
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(abspath(__file__))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Merge_Datasets:
    def __init__(self, league):
        self.league = league
        self.espn_path = ROOT_PATH + f"/Data/ESPN/{self.league}.csv"
        self.odds_path = ROOT_PATH + f"/Data/Odds/{self.league}.csv"

    def load_dfs(self):  # Top Level
        """
        loading all the datasets to be merged together
        TODO add more datasets here once I scrape them!
        """
        espn_games_df = pd.read_csv(self.espn_path)
        odds_df = pd.read_csv(self.odds_path)
        all_dfs = [espn_games_df, odds_df]
        return all_dfs

    def add_team_cols(self, df):  # Top Level
        """
        Creating Team1/Team2 columns in the dataframe based on alphabetical order
        - data sources don't always have the same home/away, especially for neutral games,
          this fixes that so we can merge on home/away nicely
        """
        df['Home_team_1'] = df['Home'] > df['Away']
        df['Team1'] = df.apply(lambda row: row['Home'] if row['Home_team_1'] else row['Away'], axis=1)
        df['Team2'] = df.apply(lambda row: row['Away'] if row['Home_team_1'] else row['Home'], axis=1)
        df.drop(['Home_team_1'], axis=1, inplace=True)
        return df

    def run(self):  # Run
        all_dfs = self.load_dfs()
        final_df = self.add_team_cols(all_dfs[0])
        for df in all_dfs[1:]:
            df = self.add_team_cols(df)
            df.drop(['Home', 'Away'], axis=1, inplace=True)
            final_df = pd.merge(final_df, df, on=['Date', 'Team1', 'Team2', 'Season'])
        final_df.drop(['Team1', 'Team2'], axis=1, inplace=True)

        final_df.sort_values(by=['Date'], inplace=True)
        final_df.to_csv(ROOT_PATH + f"/Data/{self.league}.csv", index=False)
        return final_df

    def todo_func(self):  # QA Testing
        # TODO make method to identify cols not included in the merge from ESPN, Odds, etc
        pass


if __name__ == '__main__':
    league = "NCAAB"
    x = Merge_Datasets(league)
    self = x
    x.run()
