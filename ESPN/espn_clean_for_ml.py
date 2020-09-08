# ==============================================================================
# File: espn_clean_for_ml.py
# Project: ESPN
# File Created: Sunday, 6th September 2020 3:03:57 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 7th September 2020 9:04:17 pm
# Modified By: Dillon Koch
# -----
#
# -----
# file that cleans a league's .csv for ML
# ==============================================================================


import datetime
import sys
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


tqdm.pandas()


class ESPN_Clean_For_ML:
    def __init__(self, league):
        self.league = league
        self.football_league = True if self.league in ["NFL", "NCAAF"] else False

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

    def _get_relevant_data(self, raw_rec_df, team, season, game_dt):  # Specific Helper get_records_df
        """
        finds the relevant data for any team's game in any season
        - includes games from earlier in the current season (if applicable), or
          all the games from the previous season
        """
        df = raw_rec_df.loc[raw_rec_df['Season'] == int(season)]
        df = df.loc[(df.Home == team) | (df.Away == team)]
        df = df.loc[df.datetime < game_dt]
        df = df.loc[df.Final_Status.notnull()]
        if ((len(df) == 0) and (season > 2007)):
            return self._get_relevant_data(raw_rec_df, team, season - 1, game_dt)
        return df

    def _get_team_record_vals(self, raw_rec_df, team, season, game_dt):
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

    def normalize_col(self, df, col_name):  # Top Level
        # cols to show the avg of the season so far:
            # quarter/final scores
            # team stats
        pass

    def get_target_var_df(self, original_df):  # Top Level
        pass

    def _clean_time_possession(self, original_df):  # Specific Helper clean_team_stats
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

    def _clean_dash_cols(self, original_df):  # Specific Helper clean_team_stats
        # penalties, third_down_eff, fourth_down_eff, completions_attempts, redzone_made_att,
        # sacks_yards_lost
        dash_cols = ['penalties', 'third_down_eff', 'completions_attempts', 'redzone_made_att',
                     'sacks_yards_lost']
        dash_cols = ['home_' + c for c in dash_cols] + ['away_' + c for c in dash_cols]
        for col in dash_cols:
            original_df[col] = original_df[col].fillna('0-0')

        new_dash_cols = [col + "_d1" for col in dash_cols] + [col + "_d2" for col in dash_cols]
        for col in new_dash_cols:
            original_df[col] = None

        # TODO go the self.dash_cols route to base it on whether we're dealing with a football league or not

        return original_df

    def clean_team_stats(self, original_df):  # Top Level
        if self.football_league:
            original_df = self._clean_time_possession(original_df)

        original_df = self._clean_dash_cols(original_df)

        return original_df

    def run(self):  # Run
        # scale the numeric cols
        # clean TOP col to be # seconds
        # make each row contain the season avg up until that game
        original_df = self.load_original_df()
        original_df = self.clean_team_stats(original_df)
        dummy_df = self.get_dummy_df(original_df)
        records_df = self.get_records_df(original_df)
        normalized_df = self.get_normalized_df(original_df)


if __name__ == '__main__':
    x = ESPN_Clean_For_ML("NFL")
    self = x
    # x.run()
