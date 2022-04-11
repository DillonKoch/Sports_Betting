# ==============================================================================
# File: label_predictions.py
# Project: allison
# File Created: Thursday, 7th April 2022 5:29:00 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 7th April 2022 5:29:01 pm
# Modified By: Dillon Koch
# -----
#
# -----
# adding win/loss/push labels for every prediction made
# ==============================================================================


import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Label_Predictions:
    def __init__(self, league):
        self.league = league
        self.pred_df_path = ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv"
        self.espn_df_path = ROOT_PATH + f"/Data/ESPN/{self.league}.csv"

    def _find_espn_scores(self, espn_df, home, away, date):  # Specific Helper bet_outcome
        """
        finding the scores for a game in the espn_df
        - alt_row helps with neutral games where sources mix up home/away
        """
        row = espn_df.loc[(espn_df['Home'] == home) & (espn_df['Away'] == away) & (espn_df['Date'] == date)]
        alt_row = espn_df.loc[(espn_df['Away'] == home) & (espn_df['Home'] == away) & (espn_df['Date'] == date)]
        row = pd.concat([row, alt_row])
        try:
            row = row.iloc[0, :]
        except IndexError:
            print(home, away, date)
            return None, None
        # * returning None if the game is not Final, otherwise returning ints of the scores
        if (not isinstance(row['Final_Status'], str)) and (np.isnan(row['Final_Status'])):
            return None, None
        return int(row['Home_Final']), int(row['Away_Final'])

    def _spread_outcome(self, home_score, away_score, bet_value, prediction):  # Specific Helper bet_outcome
        """
        determining if the prediction for a spread bet was correct
        """
        if (home_score + bet_value) == away_score:
            return "Push"
        home_covered = (home_score + bet_value) > away_score
        predicted_home = prediction >= 0.5
        return (home_covered and predicted_home) or (not home_covered and not predicted_home)

    def _moneyline_outcome(self, home_score, away_score, prediction):  # Specific Helper bet_outcome
        """
        determining if the prediction for a moneyline bet was correct
        """
        if home_score == away_score:
            return "Push"
        home_won = home_score > away_score
        predicted_home = prediction >= 0.5
        return (home_won and predicted_home) or (not home_won and not predicted_home)

    def _total_outcome(self, home_score, away_score, bet_value, prediction):  # Specific Helper bet_outcome
        """
        determining if the prediction for a total bet was correct
        """
        if (home_score + away_score) == bet_value:
            return "Push"
        over_won = (home_score + away_score) > bet_value
        predicted_over = prediction >= 0.5
        return (over_won and predicted_over) or (not over_won and not predicted_over)

    def bet_outcome(self, home, away, date, bet_type, bet_value, prediction, espn_df):  # Top Level
        """
        determining if a bet was correct or not
        """
        home_score, away_score = self._find_espn_scores(espn_df, home, away, date)
        if home_score is None:
            return None
        if bet_type == "Spread":
            return self._spread_outcome(home_score, away_score, bet_value, prediction)
        elif bet_type == "Moneyline":
            return self._moneyline_outcome(home_score, away_score, prediction)
        elif bet_type == "Total":
            return self._total_outcome(home_score, away_score, bet_value, prediction)

    def run(self):  # Run
        pred_df = pd.read_csv(self.pred_df_path)
        espn_df = pd.read_csv(self.espn_df_path)
        for i, row in tqdm(pred_df.iterrows()):
            if (row['Outcome'] == 'Not Labeled') or (np.isnan(row['Outcome'])):
                home = row['Home']
                away = row['Away']
                date = row['Date']
                bet_type = row['Bet_Type']
                bet_value = row['Bet_Value']
                prediction = float(row['Prediction'])
                outcome = self.bet_outcome(home, away, date, bet_type, bet_value, prediction, espn_df)
                row["Outcome"] = outcome if isinstance(outcome, str) else None if outcome is None else "Win" if outcome else "Loss"
                pred_df.iloc[i] = row
        pred_df['Outcome'].fillna('Not Labeled', inplace=True)
        pred_df.to_csv(self.pred_df_path, index=False)


if __name__ == '__main__':
    league = "NBA"
    x = Label_Predictions(league)
    self = x
    x.run()
