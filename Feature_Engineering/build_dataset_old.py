# ==============================================================================
# File: build_dataset.py
# Project: allison
# File Created: Friday, 9th December 2022 10:50:19 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 9th December 2022 10:50:20 pm
# Modified By: Dillon Koch
# -----
#
# -----
# building a ML-ready dataset to be used for training/inference
# ==============================================================================

import sys
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from Data.db_login import db_cursor
from Data.db_info import DB_Info


class Build_Dataset:
    def __init__(self, league):
        self.league = league
        self.db_info = DB_Info()
        self.db, self.cursor = db_cursor()
        self.cursor.execute("USE sports_betting;")

    # def games_df(self, past_games, team_avgs, start_date, end_date):  # Top Level
    #     cols = self.db_info.get_cols(f"ESPN_Games_{self.league}")
    #     game_info_cols = "Week, Date, Home, Away, Network, Final_Status"
    #     team_stat_cols = None  # TODO select averages here over past n games
    #     team_stat_cols = ['Home_Wins', 'Home_Losses', 'Away_Wins', 'Away_Losses'] + cols[12:]
    #     team_stat_col_str = None

    #     sql = f"""SELECT {game_info_cols}, {team_stat_cols}
    #               FROM ESPN_Games_{self.league}
    #               WHERE Date > {start_date} AND Date < {end_date};
    #               """
    #     self.cursor.execute(sql)
    #     data = self.cursor.fetchall()
    #     return pd.DataFrame(data, columns=cols)

    def _query_game_info(self, start_date, end_date):  # Specific Helper games_df
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

    def _stats_col_names(self, team_avgs, past_games):  # Helping Helper _query_team_stats
        espn_games_cols = self.db_info.get_cols(f"ESPN_Games_{self.league}")
        team_stat_cols = ['Home_Wins', 'Home_Losses', 'Away_Wins', 'Away_Losses'] + espn_games_cols[12:]
        home_cols = [col for col in team_stat_cols if col[0] == 'H']
        home_opp_cols = [col.replace('Home', 'Home_Opp') for col in home_cols]
        away_cols = [col for col in team_stat_cols if col[0] == 'A']
        away_opp_cols = [col.replace('Away', 'Away_Opp') for col in away_cols]

        all_cols = home_cols + home_opp_cols + away_cols + away_opp_cols
        if team_avgs:
            return all_cols
        else:
            output = []
            for col in all_cols:
                for i in range(past_games):
                    output.append(col + f"_{i}")
            return output

    def _single_team_stats(self, team, opp_stats, date, team_avgs, past_games):  # Helping Helper query_team_stats
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

        if team_avgs:
            home_idxs = [i + 2 for i, col in enumerate(team_stat_cols) if col[0] == 'H']
            away_idxs = [i + 2 for i, col in enumerate(team_stat_cols) if col[0] == 'A']
            stat_lists = []
            for game in data:
                if (not opp_stats and game[0] == team) or (opp_stats and not game[0] == team):
                    stat_lists.append([game[i] for i in home_idxs])
                else:
                    stat_lists.append([game[i] for i in away_idxs])

            output = []
            for i in range(40):
                vals = [float(row[i]) for row in stat_lists if row[i] is not None]
                if vals:
                    output.append(sum(vals) / len(vals))
                else:
                    output.append(None)
            return output
            # return [sum([row[i] for row in data]) / len(data) for i in range(2, 42)]

        else:
            print('here')

    def _query_team_stats(self, df, start_date, end_date, team_avgs, past_games):  # Specific Helper games_df
        stats_col_names = self._stats_col_names(team_avgs, past_games)
        stats_df = pd.DataFrame(columns=stats_col_names)
        for i in tqdm(range(len(df))):
            home = df['Home'][i]
            away = df['Away'][i]
            date = df['Date'][i].strftime('%Y%m%d')
            home_stats = self._single_team_stats(home, False, date, team_avgs, past_games)
            home_opp_stats = self._single_team_stats(home, True, date, team_avgs, past_games)
            away_stats = self._single_team_stats(away, False, date, team_avgs, past_games)
            away_opp_stats = self._single_team_stats(away, True, date, team_avgs, past_games)
            all_vals = home_stats + home_opp_stats + away_stats + away_opp_stats
            stats_df.loc[len(stats_df)] = all_vals
        stats_df.to_csv("Temp.csv", index=False)

    def games_df(self, past_games, team_avgs, start_date, end_date):  # Top Level
        # select game info
        # want to show the home team's avg team stats over last n games, and average of their opponent over last n games, same for away team
        # * process (trust)
        # have a team and game date
        # query last n games
        # make a list of team's stats and opponents' stats for each category
        # average (or not) based on 'team_avgs'
        # "Home_Final" -> "Home_Final_Avg" and "Home_Opp_Final_Avg"
        # output is a vector of team_stats, team_opp_stats
        df = self._query_game_info(start_date, end_date)
        df = self._query_team_stats(df, start_date, end_date, team_avgs, past_games)

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
            return [None] * 6
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

    def odds_to_df(self, df):  # Top Level
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

    def run(self, past_games=5, team_avgs=True, player_stats=False, player_avgs=True, start_date='20070101', end_date='21000101'):  # Run
        # creating feature vector for a single game (used for all bets - has all odds)
        # start with espn_game to get avg team stats over last n games
        # use the teams to get current players from roster (or stats from who did play if past)
        # grab avg stats from plaers, or all data (filtering out injured players)
        # insert injury data for players
        # grab past/esb betting odds for the game
        #
        df = self.games_df(past_games, team_avgs, start_date, end_date)
        # add all the other stuff we need to, then clean once
        # df = self.odds_to_df(df)


if __name__ == '__main__':
    for league in ['NFL']:
        x = Build_Dataset(league)
        self = x
        x.run()
