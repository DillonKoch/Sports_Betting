# ==============================================================================
# File: label_agents.py
# Project: allison
# File Created: Sunday, 10th April 2022 2:33:04 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 10th April 2022 2:33:04 pm
# Modified By: Dillon Koch
# -----
#
# -----
# labeling the agents' bets in /Data/Agents
# ==============================================================================


import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Data_Cleaning.label_predictions import Label_Predictions


class Label_Agents(Label_Predictions):
    def __init__(self, league):
        super(Label_Agents, self).__init__(league)
        self.agents = ['Flat', 'Dynamic']

    def bet_profit(self, wager, to_win, outcome):  # Top Level
        if outcome == "Push":
            return 0
        elif outcome is None:
            return "Not Labeled"
        elif outcome:
            return to_win
        else:
            return -wager

    def run_one(self, agent):  # Run
        agent_df = pd.read_csv(ROOT_PATH + f"/Data/Agents/{self.league}/{agent}.csv")
        espn_df = pd.read_csv(self.espn_df_path)
        for i, row in tqdm(agent_df.iterrows()):
            # if (row['Outcome'] == 'Not Labeled') or (np.isnan(row['Outcome'])):
            if row['Outcome'] not in ['Win', 'Loss', 'Push']:
                home = row['Home']
                away = row['Away']
                date = row['Date']
                bet_type = row['Bet_Type']
                bet_value = row['Bet_Value']
                # confidence = float(row['Confidence'])
                prediction = row['Prediction']
                outcome = self.bet_outcome(home, away, date, bet_type, bet_value, prediction, espn_df)
                row["Outcome"] = outcome if isinstance(outcome, str) else None if outcome is None else "Win" if outcome else "Loss"
                profit = self.bet_profit(row['Wager'], row['To_Win'], outcome)
                row['Profit'] = profit
                agent_df.iloc[i] = row
        agent_df['Outcome'].fillna('Not Labeled', inplace=True)
        agent_df.to_csv(ROOT_PATH + f"/Data/Agents/{self.league}/{agent}.csv", index=False)

    def run_all(self):  # Run
        for agent in self.agents:
            self.run_one(agent)


if __name__ == '__main__':
    league = "NBA"
    x = Label_Agents(league)
    self = x
    x.run_all()
