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


import concurrent.futures
import sys
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Data_Cleaning.match_team import Match_Team
from Data_Cleaning.player_data import Player_Data


def multithread(func, func_args):  # Multithreading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = list(tqdm(executor.map(func, func_args), total=len(func_args)))
    return result


class Merge_Datasets:
    def __init__(self, league):
        self.league = league
        self.espn_path = ROOT_PATH + f"/Data/ESPN/{self.league}.csv"
        self.odds_path = ROOT_PATH + f"/Data/Odds/{self.league}.csv"
        self.match_team = Match_Team(self.league)

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

    def _find_esb_odds(self, home, away, date, esb_df, col, close):  # Top Level
        """
        """
        rep_df = esb_df.loc[(esb_df['Home'] == home) & (esb_df['Away'] == away) & (esb_df['Date'] == date)]
        if len(rep_df) > 0:
            rep_vals = list(rep_df[col][rep_df[col].notnull()])  # if opening/closing line is null, taking the next-closest non-null value
            return None if len(rep_vals) == 0 else (rep_vals[-1] if close else rep_vals[0])

    def _update_esb_teams(self, esb_df):  # Top Level
        """
        updating the Home/Away columns in esb_df with official names from the Teams.json files
        """
        home_teams = list(set(list(esb_df['Home'])))
        home_rep_dict = {home_team: self.match_team.find_team_name(home_team) for home_team in home_teams}
        esb_df['Home'] = pd.Series([home_rep_dict[home_team] for home_team in list(esb_df['Home'])])

        away_teams = list(set(list(esb_df['Away'])))
        away_rep_dict = {away_team: self.match_team.find_team_name(away_team) for away_team in away_teams}
        esb_df['Away'] = pd.Series([away_rep_dict[away_team] for away_team in list(esb_df['Away'])])

        return esb_df

    def _update_merged_col(self, merged_df, esb_df, sbo_col, esb_col, close):  # Specific Helper
        """
        """
        missing = merged_df.loc[merged_df[sbo_col].isnull()]
        home_away_dates = [(home, away, date) for home, away, date in zip(missing['Home'], missing['Away'], missing['Date'])]
        replacements = [self._find_esb_odds(*home_away_date, esb_df, esb_col, close) for home_away_date in home_away_dates]
        for home_away_date, replacement in zip(home_away_dates, replacements):
            home, away, date = home_away_date
            merged_df.loc[(merged_df['Home'] == home) & (merged_df['Away'] == away) & (merged_df['Date'] == date), sbo_col] = replacement
        return merged_df

    def supplement_esb_odds(self, merged_df):  # Top Level
        esb_path = ROOT_PATH + f"/Data/ESB/{self.league}/Game_Lines.csv"
        esb_df = pd.read_csv(esb_path)
        esb_df = self._update_esb_teams(esb_df)

        sbo_esb_close_pairs = [('OU_Open', 'Over', False), ('OU_Open_ML', 'Over_ML', False),
                               ('OU_Close', 'Over', True), ('OU_Close_ML', 'Over_ML', True),
                               ('Home_Line_Open', 'Home_Spread', False), ('Home_Line_Open_ML', 'Home_Spread_ML', False),
                               ('Away_Line_Open', 'Away_Spread', False), ('Away_Line_Open_ML', 'Away_Spread_ML', False),
                               ('Home_Line_Close', 'Home_Spread', True), ('Home_Line_Close_ML', 'Home_Spread_ML', True),
                               ('Away_Line_Close', 'Away_Spread', True), ('Away_Line_Close_ML', 'Away_Spread_ML', True),
                               ('Home_ML', 'Home_ML', True), ('Away_ML', 'Away_ML', True)]

        for sbo_esb_close_pair in tqdm(sbo_esb_close_pairs):
            sbo_col, esb_col, close = sbo_esb_close_pair
            merged_df = self._update_merged_col(merged_df, esb_df, sbo_col, esb_col, close)

        return merged_df

    def supplement_player_stats(self, final_df):  # Top Level
        # I have the team/date, just run the player_data.py script to get the player stats and add them
        # ! have to multithread the hell out of this
        home_teams = list(final_df['Home'])
        away_teams = list(final_df["Away"])
        dates = list(final_df['Date'])

        new_df_cols = ['Home', 'Away', 'Date'] + ["H" + item for item in self.player_data.feature_col_names] + ['A' + item for item in self.player_data.feature_col_names]
        new_df = pd.DataFrame(columns=new_df_cols)

        # home_stats = [self.player_data.run(home, date) for home, date in tqdm(zip(home_teams, dates))]
        # away_stats = [self.player_data.run(away, date) for away, date in tqdm(zip(away_teams, dates))]
        def run_player_data(args):
            team, date = args
            return self.player_data.run(team, date)
        home_inputs = [(home_team, date) for home_team, date in zip(home_teams, dates)]
        home_stats = multithread(run_player_data, home_inputs)
        away_inputs = [(away_team, date) for away_team, date in zip(away_teams, dates)]
        away_stats = multithread(run_player_data, away_inputs)
        for i, (home, home_stat, away, away_stat, date) in enumerate(zip(home_teams, home_stats, away_teams, away_stats, dates)):
            new_df.loc[len(new_df)] = [home, away, date] + home_stat + away_stat

        # for i, (home, away, date) in enumerate(zip(home_teams, away_teams, dates)):
        #     print(i)
        #     home_stats = self.player_data.run(home, date)
        #     away_stats = self.player_data.run(away, date)
        #     new_df.loc[len(new_df)] = [home, away, date] + home_stats + away_stats

        final_df = pd.merge(final_df, new_df, how='left', on=['Home', 'Away', 'Date'])
        return final_df

    def run(self):  # Run
        all_dfs = self.load_dfs()
        final_df = self.add_team_cols(all_dfs[0])
        for df in all_dfs[1:]:
            df = self.add_team_cols(df)
            df.drop(['Home', 'Away'], axis=1, inplace=True)
            final_df = pd.merge(final_df, df, how='left', on=['Date', 'Team1', 'Team2', 'Season'])
        final_df.drop(['Team1', 'Team2'], axis=1, inplace=True)

        final_df = self.supplement_esb_odds(final_df)
        # final_df = self.supplement_player_stats(final_df)
        final_df.sort_values(by=['Date'], inplace=True)
        final_df.to_csv(ROOT_PATH + f"/Data/{self.league}.csv", index=False)
        return final_df

    def todo_func(self):  # QA Testing
        # TODO make method to identify cols not included in the merge from ESPN, Odds, etc
        pass


if __name__ == '__main__':
    # for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
    for league in ['NCAAB']:
        print(league)
        x = Merge_Datasets(league)
        self = x
        x.run()
