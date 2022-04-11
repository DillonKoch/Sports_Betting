# ==============================================================================
# File: banker.py
# Project: allison
# File Created: Tuesday, 30th November 2021 9:01:08 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 30th November 2021 9:01:10 pm
# Modified By: Dillon Koch
# -----
#
# -----
# evaluating the bets made in /Data/Agent_Bets and awarding/subtracting money
# ==============================================================================


import os
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
import datetime

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class Banker:
    def __init__(self, league):
        self.league = league

    def load_agent_df_paths(self):  # Top Level
        """
        loading all the agent df paths for the banker to bank
        """
        folder = ROOT_PATH + f"/Data/Agent_Bets/{self.league}/"
        files = listdir_fullpath(folder)
        df_paths = [file for file in files if '.csv' in file]
        return df_paths

    def _home_away_score(self, home, away, date, game_df):  # Specific Helper bank_agent_df
        """
        finding the home/away scores for a game in game_df, or None if it hasn't been played
        """
        game = game_df.loc[(game_df['Home'] == home) & (game_df['Away'] == away) & (game_df['Date'] == date)]
        if not isinstance(game['Final_Status'].values[0], str):
            return None, None
        else:
            return game['Home_Final'].values[0], game['Away_Final'].values[0]

    def _check_bet_won(self, row, home_score, away_score):  # Specific Helper bank_agent_df
        bet_type = row['Bet_Type'].values[0]

        if bet_type == "Spread":
            bet_home = row['Models_Pred'].values[0] > 0.5
            spread = row['Bet_Val'].values[0]
            home_covered = (home_score + spread) > away_score
            bet_won = (bet_home and home_covered) or (not bet_home and not home_covered)

        elif bet_type == "Moneyline":
            bet_home = row['Models_Pred'].values[0] > 0.5
            home_won = home_score > away_score
            bet_won = (bet_home and home_won) or (not bet_home and not home_won)

        elif bet_type == "Total":
            total = float(row['Bet_Val'].values[0])
            over_won = (home_score + away_score) > total
            bet_over = float(row['Models_Pred'].values[0]) > 0.5
            bet_won = (over_won and bet_over) or (not over_won and not bet_over)

        return bet_won

    def bank_agent_df(self, agent_df, game_df):  # Top Level
        """
        updating the agent_df with results from game_df
        """
        today_date_str = datetime.datetime.now().strftime("%Y-%m-%d")
        for i, row in agent_df.iterrows():
            # * skipping rows we've already banked, or unplayed games
            if (not np.isnan(row['Outcome']) or row['Date'] > today_date_str):
                continue

            home_score, away_score = self._home_away_score(row['Home'], row['Away'], row['Date'], game_df)
            bet_won = self._check_bet_won(row, home_score, away_score)

            # ? unsure if this updates in place inside the df
            row['Outcome'] = 1 if bet_won else 0
            row['Profit'] = row['To_Win'] if bet_won else 0
            row['Running_Profit'] = None
        return agent_df

    def run(self):  # Run
        game_df = pd.read_csv(ROOT_PATH + f"/Data/{self.league}.csv")
        agent_df_paths = self.load_agent_df_paths()
        for agent_df_path in agent_df_paths:
            agent_df = pd.read_csv(agent_df_path)
            new_agent_df = self.bank_agent_df(agent_df, game_df)
            new_agent_df.to_csv(agent_df_path, index=False)
            print(f"Saved {agent_df_path}")
        print("DONE")


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        x = Banker(league)
        self = x
        x.run()
