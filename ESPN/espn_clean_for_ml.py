# ==============================================================================
# File: espn_clean_for_ml.py
# Project: ESPN
# File Created: Sunday, 6th September 2020 3:03:57 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 12th September 2020 10:24:01 am
# Modified By: Dillon Koch
# -----
#
# -----
# file that cleans a league's .csv for ML
# ==============================================================================


import copy
import datetime
import sys
import warnings
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

warnings.filterwarnings('ignore')

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


tqdm.pandas()


class ESPN_Clean_For_ML:
    def __init__(self, league):
        self.league = league
        self.football_league = True if self.league in ["NFL", "NCAAF"] else False

    @property
    def original_dash_cols(self):  # Property
        if self.football_league:
            cols = ['penalties', 'third_down_eff', 'fourth_down_eff', 'completions_attempts', 'redzone_made_att',
                    'sacks_yards_lost']
        else:
            cols = ['field_goals', 'three_pointers', 'free_throws', ]

        # creating final list with all home, then all away...
        home_cols = ['home_' + col for col in cols]
        away_cols = ['away_' + col for col in cols]
        final_cols = home_cols + away_cols
        return final_cols

    @property
    def new_dash_cols(self):  # Property
        cols = self.original_dash_cols
        new_cols = []
        for col in cols:
            new_cols.append(col + "_d1")
            new_cols.append(col + "_d2")
        return new_cols

    @property
    def score_cols(self):  # Property
        if self.league == "NCAAB":
            cols = ['H1H', 'H2H', 'HOT', 'Home_Score', 'A1H', 'A2H', 'AOT', 'Away_Score']
        else:
            cols = ['HQ1', 'HQ2', 'HQ3', 'HQ4', 'HOT', 'Home_Score',
                    'AQ1', 'AQ2', 'AQ3', 'AQ4', 'AOT', 'Away_Score']
        return cols

    @property
    def opposite_score_dict(self):  # Property
        dic = {
            "HQ1": "AQ1",
            "HQ2": "AQ2",
            "HQ3": "AQ3",
            "HQ4": "AQ4",
            "HOT": "AOT",
            "Home_Score": "Away_Score",
            "AQ1": "HQ1",
            "AQ2": "HQ2",
            "AQ3": "HQ3",
            "AQ4": "HQ4",
            "AOT": "HOT",
            "Away_Score": "Home_Score"
        }
        return dic

    def _get_relevant_data(self, df, team, season, game_dt):  # Global Helper
        """
        finds the relevant data for any team's game in any season
        - includes games from earlier in the current season (if applicable), or
          all the games from the previous season
        """
        og_df = copy.deepcopy(df)
        df = df.loc[df['Season'] == int(season)]
        df = df.loc[(df.Home == team) | (df.Away == team)]
        df = df.loc[df.datetime < game_dt]
        df = df.loc[df.Final_Status.notnull()]
        if ((len(df) == 0) and (season > 2007)):
            return self._get_relevant_data(og_df, team, season - 1, game_dt)
        return df

    def load_original_df(self):  # Top Level
        df = pd.read_csv(ROOT_PATH + f"/ESPN/Data/{self.league}.csv")
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['datetime'] = df['datetime'].dt.date
        return df

    def get_dummy_df(self, original_df):  # Top Level
        """
        creates a df based on the original espn df with one hot encoded columns
        from the categorical columns
        """
        dummy_cols = ['Home', 'Away', 'Network']
        dummy_df = pd.get_dummies(original_df[dummy_cols])
        return dummy_df

    def _get_raw_record_df(self, original_df):  # Specific Helper get_records_df
        """
        returns a subset of original_df with the necessary columns to create the
        ML-friendly team record columns
        """
        record_cols = ['datetime', 'Season', 'Home', 'Away', 'Home_Record', 'Away_Record',
                       'Home_Score', 'Away_Score', 'Final_Status']
        record_df = original_df.loc[:, record_cols]
        today = datetime.date.today()
        record_df = record_df.loc[record_df['datetime'] < today]
        record_df['neutral'] = record_df.apply(lambda row: 'Home' not in str(row['Home_Record']), axis=1)
        record_df['conf'] = record_df.apply(lambda row: 'Conf' in str(row['Home_Record']), axis=1)
        record_df['home_won'] = record_df.apply(lambda row: int(row['Home_Score']) > int(row['Away_Score']), axis=1)
        record_df['away_won'] = record_df.apply(lambda row: int(row['Home_Score']) < int(row['Away_Score']), axis=1)
        record_df['tie'] = record_df.apply(lambda row: int(row['Home_Score']) == int(row['Away_Score']), axis=1)
        return record_df

    def _init_new_record_df(self, original_df):  # Specific Helper get_records_df
        """
        creates a df with datetime/Home/Away from original_df, as well as
        empty columns for all the ML record data to be inserted into
        """
        original_cols = ['datetime', 'Season', 'Home', 'Away', 'Home_Record', 'Away_Record']
        df = original_df.loc[:, original_cols]

        col_types = ['ovr', 'home', 'away', 'neutral', 'conf']
        cols = [ct + '_wins' for ct in col_types] + [ct + '_losses' for ct in col_types] + [ct + "_ties" for ct in col_types]
        all_cols = ['home_' + col for col in cols] + ['away_' + col for col in cols]
        for col in all_cols:
            df[col] = None
        return df

    def _get_team_record_vals(self, raw_rec_df, team, season, game_dt):  # Specific Helper get_records_df
        df = self._get_relevant_data(raw_rec_df, team, season, game_dt)
        home_df = df.loc[(df.Home == team) & (df.neutral == False)]
        away_df = df.loc[(df.Away == team) & (df.neutral == False)]
        conf_df = df.loc[df.conf == True]
        neutral_df = df.loc[df.neutral == True]

        home_wins = home_df['home_won'].sum()
        home_losses = home_df['away_won'].sum()
        home_ties = home_df['tie'].sum()

        away_wins = away_df['away_won'].sum()
        away_losses = away_df['home_won'].sum()
        away_ties = away_df['tie'].sum()

        conf_home_wins = len(conf_df.loc[(conf_df.Home == team) & (conf_df.home_won == True)])
        conf_away_wins = len(conf_df.loc[(conf_df.Away == team) & (conf_df.away_won == True)])
        conf_wins = conf_home_wins + conf_away_wins

        conf_home_losses = len(conf_df.loc[(conf_df.Home == team) & (conf_df.home_won == True)])
        conf_away_losses = len(conf_df.loc[(conf_df.Away == team) & (conf_df.away_won == True)])
        conf_losses = conf_home_losses + conf_away_losses

        neutral_home_wins = len(neutral_df.loc[(neutral_df.Home == team) & (neutral_df.home_won == True)])
        neutral_away_wins = len(neutral_df.loc[(neutral_df.Away == team) & (neutral_df.away_won == True)])
        neutral_wins = neutral_home_wins + neutral_away_wins

        neutral_home_losses = len(neutral_df.loc[(neutral_df.Home == team) & (neutral_df.home_won == True)])
        neutral_away_losses = len(neutral_df.loc[(neutral_df.Away == team) & (neutral_df.away_won == True)])
        neutral_losses = neutral_home_losses + neutral_away_losses

        conf_ties = conf_df['tie'].sum()
        neutral_ties = neutral_df['tie'].sum()
        ovr_ties = home_ties + away_ties + neutral_ties

        ovr_wins = home_wins + away_wins + neutral_wins
        ovr_losses = home_losses + away_losses + neutral_losses

        return (ovr_wins, home_wins, away_wins, neutral_wins, conf_wins,
                ovr_losses, home_losses, away_losses, neutral_losses, conf_losses,
                ovr_ties, home_ties, away_ties, neutral_ties, conf_ties)

    def get_records_df(self, original_df):  # Top Level
        """
        creates a df with record columns ready for ML based on original_df
        """
        raw_rec_df = self._get_raw_record_df(original_df)
        new_record_df = self._init_new_record_df(original_df)
        home_cols = [c for c in list(new_record_df.columns) if c[:4] == 'home']
        away_cols = [c for c in list(new_record_df.columns) if c[:4] == 'away']

        def update_row_records(row):
            home_team = row['Home']
            away_team = row['Away']
            season = int(row['Season'])
            game_date = row['datetime']

            home_record_vals = self._get_team_record_vals(raw_rec_df, home_team, season, game_date)
            away_record_vals = self._get_team_record_vals(raw_rec_df, away_team, season, game_date)
            row[home_cols] = home_record_vals
            row[away_cols] = away_record_vals
            return row

        new_record_df = new_record_df.progress_apply(lambda row: update_row_records(row), axis=1)
        return new_record_df

    def _clean_dash_cols(self, original_df):  # Specific Helper clean_team_stats
        """
        changes the original_df from having the original dash columns to two new dash columns per original,
        with the d1 and d2 values in each column
        - also gets rid of the old original dash cols
        """
        # create empty new dash cols
        for col in self.new_dash_cols:
            original_df[col] = None

        def split_dash_col(row, col_name):
            val = row[col_name]
            d1_col = col_name + '_d1'
            d2_col = col_name + '_d2'
            d1, d2 = val.split('-')
            row[d1_col] = d1
            row[d2_col] = d2
            return row

        # populate new dash cols
        for col in tqdm(self.original_dash_cols):
            original_df[col].fillna('0-0', inplace=True)
            original_df = original_df.apply(lambda row: split_dash_col(row, col), axis=1)
            original_df.drop([col], axis=1, inplace=True)

        return original_df

    def _clean_time_possession(self, original_df):  # Specific Helper get_team_stats_df
        original_df['home_possession'] = original_df['home_possession'].fillna("30:00")
        original_df['away_possession'] = original_df['away_possession'].fillna("30:00")

        def clean_row_TOP(row):
            for col in ['home', 'away']:
                col_name = "{}_possession".format(col)
                top_str = row[col_name]
                minutes, seconds = top_str.split(":")
                total_seconds = (int(minutes) * 60) + int(seconds)
                row[col_name] = total_seconds
            return row
        original_df = original_df.apply(lambda row: clean_row_TOP(row), axis=1)
        return original_df

    def _get_stats_cols(self, original_df):  # Specific Helper get_team_stats_df
        """
        creates a list of all the stats columns to be created for the ML-ready dataframe
        """
        df_cols = list(original_df.columns)
        stats_cols = df_cols[df_cols.index("League"):]
        stats_cols = [c for c in stats_cols if c not in ["League", "datetime"]]

        # remove original dash cols and add the d1/d2 cols
        stats_cols = [c for c in stats_cols if c not in self.original_dash_cols]
        stats_cols += self.new_dash_cols

        return ['datetime', 'Season', 'Home', 'Away'] + stats_cols

    def _get_stat_avg(self, df, col, team):  # Specific Helper get_team_stats_df
        home_df = df.loc[df.Home == team]
        away_df = df.loc[df.Away == team]
        home_vals = list(home_df['home_' + col])
        away_vals = list(away_df['away_' + col])
        all_vals = home_vals + away_vals
        all_vals = [float(val) for val in all_vals]
        avg = np.average(all_vals) if len(all_vals) > 0 else np.nan
        return avg

    def get_team_stats_df(self, original_df):  # Top Level
        original_df = self._clean_dash_cols(original_df)
        if self.football_league:
            original_df = self._clean_time_possession(original_df)
        stat_cols = self._get_stats_cols(original_df)
        stats_df = original_df.loc[:, stat_cols]

        non_team_stat_cols = [col.replace('home_', '').replace('away_', '') for col in stat_cols]
        update_cols = []
        for col in non_team_stat_cols:
            if col not in update_cols:
                if col not in ['datetime', 'Season', 'Home', 'Away']:
                    update_cols.append(col)

        def update_row_stats(row):
            home = row['Home']
            away = row['Away']
            season = row['Season']
            game_dt = row['datetime']
            home_df = self._get_relevant_data(original_df, home, season, game_dt)
            away_df = self._get_relevant_data(original_df, away, season, game_dt)

            for col in update_cols:
                home_avg = self._get_stat_avg(home_df, col, home)
                away_avg = self._get_stat_avg(away_df, col, away)
                row['home_' + col] = home_avg
                row['away_' + col] = away_avg

            return row

        stats_df = stats_df.progress_apply(lambda row: update_row_stats(row), axis=1)
        return stats_df

    def _get_score_avg(self, df, col, team):  # Specific Helper get_score_df
        home_df = df.loc[df.Home == team]
        away_df = df.loc[df.Away == team]

        home_col = 'H' + col if col != '_Score' else 'Home' + col
        away_col = 'A' + col if col != '_Score' else 'Away' + col

        home_vals = list(home_df[home_col])
        away_vals = list(away_df[away_col])
        all_vals = home_vals + away_vals
        all_vals = [float(val) for val in all_vals]
        all_vals = [val for val in all_vals if str(val) != 'nan']
        # all_vals = [0] if len(all_vals) == 0 else all_vals
        avg = np.average(all_vals)
        return avg

    def get_score_df(self, original_df):  # Top Level
        raw_score_cols = ['Q1', 'Q2', 'Q3', 'Q4', 'OT', '_Score']
        score_cols = ['datetime', 'Season', 'Home', 'Away'] + self.score_cols
        score_df = original_df.loc[:, score_cols]

        def update_row_scores(row):
            home = row['Home']
            away = row['Away']
            season = row['Season']
            game_dt = row['datetime']
            home_df = self._get_relevant_data(original_df, home, season, game_dt)
            away_df = self._get_relevant_data(original_df, away, season, game_dt)

            for col in raw_score_cols:
                home_avg = self._get_score_avg(home_df, col, home)
                away_avg = self._get_score_avg(away_df, col, away)
                home_col = 'H' + col if col != '_Score' else 'Home' + col
                away_col = 'A' + col if col != '_Score' else 'Away' + col

                row[home_col] = home_avg
                row[away_col] = away_avg

            return row

        score_df = score_df.progress_apply(lambda row: update_row_scores(row), axis=1)
        score_df['HOT'].fillna(0, inplace=True)
        score_df['AOT'].fillna(0, inplace=True)
        return score_df

    def get_target_df(self, original_df):  # Top Level
        target_cols = ['Home_Score', 'Away_Score', 'Line', 'Over_Under']
        target_df = original_df.loc[:, target_cols]
        return target_df

    def merge_dfs(self, dummy_df, records_df, team_stats_df, score_df, target_df):  # Top Level

        full_df = pd.concat([records_df, team_stats_df, score_df, dummy_df, target_df], axis=1)
        full_df = full_df.loc[:, ~full_df.columns.duplicated()]
        return full_df

    def run(self, save=True):  # Run
        # scale the numeric cols
        # clean TOP col to be # seconds
        # make each row contain the season avg up until that game
        original_df = self.load_original_df()

        # temp
        # original_df = original_df.loc[original_df.Season >= 2018, :]

        # end temp
        dummy_df = self.get_dummy_df(original_df)
        print('getting record df...')
        records_df = self.get_records_df(original_df)
        print('getting team stats df...')
        team_stats_df = self.get_team_stats_df(original_df)
        print('getting score df...')
        score_df = self.get_score_df(original_df)
        target_df = self.get_target_df(original_df)
        full_df = self.merge_dfs(dummy_df, records_df, team_stats_df, score_df, target_df)
        if save:
            full_df.to_csv(ROOT_PATH + f"/ESPN/ML/{self.league}_ML.csv", index=False)
        return full_df


if __name__ == '__main__':
    x = ESPN_Clean_For_ML("NBA")
    self = x
    x.run()

    # original_df = self.load_original_df()
    # team_stats_df = self.get_team_stats_df(original_df)
    # original_df = self.load_original_df()
    # x._get_relevant_data(original_df, "Minnesota Vikings", 2008, datetime.date(2008, 9, 4))
