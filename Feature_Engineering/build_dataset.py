# ==============================================================================
# File: build_dataset.py
# Project: allison
# File Created: Monday, 12th December 2022 8:42:24 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 12th December 2022 8:42:41 pm
# Modified By: Dillon Koch
# -----
#
# -----
# building training datasets
# ==============================================================================

import sys
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Data.db_info import DB_Info
from Data.db_login import db_cursor


class Build_Dataset:
    def __init__(self, league):
        self.league = league
        self.db_info = DB_Info()
        self.db, self.cursor = db_cursor()
        self.cursor.execute("USE sports_betting;")

    def _game_info(self, start_date, end_date):  # Specific Helper games_df
        """
        querying basic game info for every game in the ESPN_Games_{league} table
        """
        sql = f"""SELECT Date, Home, Away, Week, Network, Final_Status FROM ESPN_Games_{self.league}
                WHERE Home != 'Kennedy Cougars' AND Date <= CURDATE()
                AND Date >= {start_date} AND Date <= {end_date};"""
        self.cursor.execute(sql)
        data = [list(item) for item in self.cursor.fetchall()]
        df = pd.DataFrame(data, columns=['Date', 'Home', 'Away', 'Week', 'Network', 'Final_Status'])
        return df

    def _add_team_stats_cols(self, df):  # Helping Helper _add_team_stats
        espn_games_cols = self.db_info.get_cols(f"ESPN_Games_{self.league}")
        home_cols = [col for col in espn_games_cols if col.startswith("Home_")]
        home_opp_cols = [col.replace("Home_", "Home_Opp_") for col in home_cols]
        away_cols = [col for col in espn_games_cols if col.startswith("Away_")]
        away_opp_cols = [col.replace("Away_", "Away_Opp_") for col in away_cols]

        all_cols = home_cols + home_opp_cols + away_cols + away_opp_cols
        for col in all_cols:
            df[col] = None
        return df

    def _avg_vals(self, val_lists):  # Helping Helper _data_to_vector
        output = []
        for i in range(40):
            vals = [float(row[i]) for row in val_lists if row[i] is not None]
            if vals:
                output.append(sum(vals) / len(vals))
            else:
                output.append(None)
        return output

    def _data_to_vector(self, data, team_stat_cols, team, team_avgs, opp_stats):  # Helping Helper _team_stats_vector
        val_lists = []
        for row in data:
            cur_val_list = []
            add_home = (row[0] == team and not opp_stats) or (row[0] != team and opp_stats)
            for col_name, val in zip(team_stat_cols, row[2:]):
                if col_name.startswith("Home_") and add_home:
                    cur_val_list.append(val)
                elif col_name.startswith("Away_") and not add_home:
                    cur_val_list.append(val)
            val_lists.append(cur_val_list)

        return self._avg_vals(val_lists) if team_avgs else [subitem for item in val_lists for subitem in item]

    def _team_stats_vector(self, team, date, team_avgs, past_games, opp_stats=False):  # Helping Helper _add_team_stats
        """
        """
        espn_games_cols = self.db_info.get_cols(f"ESPN_Games_{self.league}")
        team_stat_cols = ['Home_Wins', 'Home_Losses', 'Away_Wins', 'Away_Losses'] + espn_games_cols[12:]
        cols_str = ", ".join(team_stat_cols)
        sql = f"""SELECT Home, Away, {cols_str} FROM ESPN_Games_{self.league}
                  WHERE Date < {date} AND (Home = '{team}' OR Away = '{team}')
                  ORDER BY Date DESC LIMIT {past_games};"""
        self.cursor.execute(sql)
        data = self.cursor.fetchall()

        if len(data) < past_games:
            return [None] * 40

        return self._data_to_vector(data, team_stat_cols, team, team_avgs, opp_stats)

    def _add_team_stats(self, df, team_avgs, past_games):  # Specific Helper games_df
        # add column names to df (avgs or all separate) - (home, home_opp, away, away_opp)
        # loop through df, query data for the 4 scenarios^

        df = self._add_team_stats_cols(df)
        for i in tqdm(range(len(df))):
            home = df['Home'][i]
            away = df['Away'][i]
            date = df['Date'][i].strftime("%Y%m%d")
            home_stats = self._team_stats_vector(home, date, team_avgs, past_games)
            home_opp_stats = self._team_stats_vector(home, date, team_avgs, past_games, opp_stats=True)
            away_stats = self._team_stats_vector(away, date, team_avgs, past_games)
            away_opp_stats = self._team_stats_vector(away, date, team_avgs, past_games, opp_stats=True)
            df.loc[i] = list(df.iloc[i, :6]) + home_stats + home_opp_stats + away_stats + away_opp_stats
            if i == 100:  # ! REMOVE
                break
        return df

    def games_df(self, start_date, end_date, past_games, team_avgs):  # Top Level
        df = self._game_info(start_date, end_date)
        df = self._add_team_stats(df, team_avgs, past_games)
        return df

    def _sbro_odds(self, date_str, home, away):  # Specific Helper odds_to_df
        """
        querying odds (new_cols from odds_to_df) from SBRO table
        """
        sql = f"""SELECT OU_Close, OU_Close_ML, OU_Close, OU_Close_ML,
            Home_Line_Close, Home_Line_Close_ML, Away_Line_Close, Away_Line_Close_ML,
            Home_ML, Away_ML
            FROM SBRO_{self.league}
            WHERE Home = '{home}' AND Away = '{away}'
            AND Date = '{date_str}';"""
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        if not data:
            return [None] * 10
        else:
            return list(data[0])

    def _esb_odds(self, date_str, home, away):  # Specific Helper odds_to_df
        """
        querying odds (new_cols from odds_to_df) from ESB table
        """
        sql = f"""SELECT Over_Odds, Over_ML, Under_Odds, Under_ML, Home_Spread, Home_Spread_ML,
                  Away_Spread, Away_Spread_ML, Home_ML, Away_ML
                  FROM ESB_{self.league}
                  WHERE Home = '{home}' AND Away = '{away}'
                  AND Date = '{date_str}';"""
        self.cursor.execute(sql)
        data = self.cursor.fetchall()
        if not data:
            return [None] * 10
        else:
            return list(data[0])

    def add_betting_odds(self, df):  # Top Level
        """
        adding odds data to the df from either SBRO odds or ESB
        """
        new_cols = ['Over_Odds', 'Over_ML', 'Uner_Odds', 'Under_ML',
                    'Home_Line', 'Home_Line_ML', 'Away_Line', 'Away_Line_ML', 'Home_ML', 'Away_ML']
        for col in new_cols:
            df[col] = None

        dates = [item.strftime('%Y%m%d') for item in df['Date']]
        homes = list(df['Home'])
        aways = list(df['Away'])
        for i, (date, home, away) in tqdm(enumerate(zip(dates, homes, aways))):
            odds = self._sbro_odds(date, home, away)
            if any([item is None for item in odds]):
                odds = self._esb_odds(date, home, away)
            df.iloc[i, -10:] = odds

        return df

    def add_player_stats(self, df):  # Top Level
        # add cols to df (once)
        # use player_stats class to get vector to insert to df (once per team per row)
        # (home_avg_player_stats, home_opp_avg_player_stats, away, away_opp)
        pass

    def run(self, past_games=5, team_avgs=True, player_stats=False, player_avgs=True, start_date='20070101', end_date='21000101'):  # Run
        df = self.games_df(start_date, end_date, past_games, team_avgs)
        df = self.add_betting_odds(df)
        df = self.add_player_stats(df)

        df.to_csv(ROOT_PATH + f"/{self.league}.csv", index=False)


if __name__ == '__main__':
    # for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
    for league in ['NFL']:
        x = Build_Dataset(league)
        self = x
        x.run()
