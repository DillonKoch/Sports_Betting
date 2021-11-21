# ==============================================================================
# File: label_predictions.py
# Project: allison
# File Created: Saturday, 20th November 2021 8:40:02 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 20th November 2021 8:40:03 pm
# Modified By: Dillon Koch
# -----
#
# -----
# <<<FILE DESCRIPTION>>>
# ==============================================================================


import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Label_Predictions:
    def __init__(self, league):
        self.league = league

    def load_pred_df(self):  # Top Level
        """
        loading the df with predictions made by the models
        """
        path = ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv"
        df = pd.read_csv(path)
        return df

    def load_espn_df(self):  # Top Level
        """
        loading the ESPN games.csv file with game outcomes, to be used for labeling predictions
        """
        path = ROOT_PATH + f"/Data/ESPN/{self.league}/Games.csv"
        df = pd.read_csv(path)
        return df

    def _find_espn_scores(self, espn_df, home, away, date):  # Specific Helper bet_outcome
        row = espn_df.loc[(espn_df['Home'] == home) & (espn_df['Away'] == away) & (espn_df['Date'] == date)]
        row = row.iloc[0, :]
        # * returning None if the game is not Final, otherwise returning ints of the scores
        if np.isnan(row['Final_Status']):
            return None, None
        return int(row['Home_Final']), int(row['Away_Final'])

    def _spread_outcome(self, home_score, away_score, bet_value, prediction):  # Specific Helper bet_outcome
        """
        determining if the prediction for a spread bet was correct
        """
        home_covered = (home_score + bet_value) > away_score
        predicted_home = prediction >= 0.5
        return (home_covered and predicted_home) or (not home_covered and not predicted_home)

    def _moneyline_outcome(self, home_score, away_score, prediction):  # Specific Helper bet_outcome
        """
        determining if the prediction for a moneyline bet was correct
        """
        home_won = home_score > away_score
        predicted_home = prediction >= 0.5
        return (home_won and predicted_home) or (not home_won and not predicted_home)

    def _total_outcome(self, home_score, away_score, bet_value, prediction):  # Specific Helper bet_outcome
        """
        determining if the prediction for a total bet was correct
        """
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
        pred_df = self.load_pred_df()
        espn_df = self.load_espn_df()
        for i, row in pred_df.iterrows():
            if np.isnan(row['Outcome']):
                home = row['Home']
                away = row['Away']
                date = row['Game_Date']
                bet_type = row['Bet_Type']
                bet_value = row['Bet_Value']
                prediction = float(row['Prediction'])
                outcome = self.bet_outcome(home, away, date, bet_type, bet_value, prediction, espn_df)
                row["Outcome"] = outcome
        pred_df.to_csv(ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv", index=False)
        print("PREDICTIONS LABELED!")


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        x = Label_Predictions(league)
        self = x
        x.run()