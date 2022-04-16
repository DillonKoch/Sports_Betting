# ==============================================================================
# File: alt_odds.py
# Project: allison
# File Created: Thursday, 14th April 2022 11:28:51 am
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 14th April 2022 11:28:52 am
# Modified By: Dillon Koch
# -----
#
# -----
# running the models on alternative odds
# ==============================================================================


import copy
import datetime
import os
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Modeling.run_models import Run_Models


class Alt_Odds(Run_Models):
    def __init__(self, league, bet_type):
        super(Alt_Odds, self).__init__(league, bet_type)
        self.odd_val = "Home_Line_Close" if bet_type == "Spread" else "OU_Close"

    def _alt_odds(self, odds_val):   # Helping Helper _expand_df_alt_odds
        alt_odds = [odds_val - 5, odds_val - 4, odds_val - 3, odds_val - 2.5,
                    odds_val - 2, odds_val - 1.5, odds_val - 1, odds_val - 0.5,
                    odds_val, odds_val + 0.5, odds_val + 1, odds_val + 1.5,
                    odds_val + 2, odds_val + 2.5, odds_val + 3, odds_val + 4, odds_val + 5]
        return alt_odds

    def _expand_df_alt_odds(self, df):  # Specific Helper upcoming_games
        exp_df = pd.DataFrame(columns=list(df.columns))
        for i in tqdm(range(len(df))):
            exp_df.loc[len(exp_df)] = df.loc[i]
            odds_val = df.loc[i, self.odd_val]
            alt_odds = self._alt_odds(odds_val)
            for alt_odd in alt_odds:
                new_row = copy.deepcopy(df.loc[i])
                new_row[self.odd_val] = alt_odd
                exp_df.loc[len(exp_df)] = new_row
        return exp_df

    def upcoming_games(self, df, scaler):  # Top Level
        df['Date'] = pd.to_datetime(df['Date'])
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        df = df.loc[df['Date'] > yesterday]
        odds_cols = ['Home_Line_Close', 'Home_Line_Close_ML', 'OU_Close', 'OU_Close_ML', 'Home_ML', 'Away_ML']
        df = df.dropna(subset=odds_cols, axis=0)
        df.reset_index(drop=True, inplace=True)
        df = self._expand_df_alt_odds(df)
        X_cols = [col for col in list(df.columns) if col not in (['Home', 'Away', "Date"] + self.all_target_cols)]
        X = np.array(df[X_cols])
        X = scaler.transform(X)
        X = torch.from_numpy(X).float().to('cuda')
        return df, X

    def load_alt_df(self):  # Top Level
        path = ROOT_PATH + f"/Data/Predictions/{self.league}/Alt_Predictions.csv"
        if not os.path.exists(path):
            cols = ['Date', 'Home', 'Away', 'Bet_Type', 'Bet_Value', 'Bet_ML', 'Prediction', 'Outcome', "Pred_ts"]
            df = pd.DataFrame(columns=cols)
        else:
            df = pd.read_csv(path)
        return df

    def update_alt_df(self, alt_df, pred, modeling_df):  # Top Level
        date = modeling_df['Date'].strftime('%Y-%m-%d')
        home = modeling_df['Home']
        away = modeling_df['Away']
        bet_val = modeling_df[self.bet_val_dict[self.bet_type]]
        bet_val_ml = modeling_df[self.bet_val_ml_dict[self.bet_type]]
        pred = round(pred.item(), 3)
        new_row = [date, home, away, self.bet_type, bet_val, bet_val_ml, pred, None, self._current_ts()]
        alt_df.loc[len(alt_df)] = new_row
        return alt_df

    def run(self):  # Run
        model, model_path = self.load_model()
        modeling_df = self.load_modeling_df(model_path)
        scaler = self.load_scaler(model_path)
        modeling_df, X = self.upcoming_games(modeling_df, scaler)
        # expanded_modeling_df = self.expand_modeling_df(modeling_df)
        alt_df = self.load_alt_df()
        for i in range(len(modeling_df)):
            current_X = X[i]
            pred = model(current_X)
            alt_df = self.update_alt_df(alt_df, pred, modeling_df.iloc[i, :])
        alt_df.drop_duplicates(subset=['Date', 'Home', 'Away', 'Bet_Type', 'Bet_Value', 'Bet_ML'], keep='last', inplace=True)
        alt_df.to_csv(ROOT_PATH + f"/Data/Predictions/{self.league}/Alt_Predictions.csv", index=False)


if __name__ == '__main__':
    league = 'NBA'
    for bet_type in ['Spread', 'Total']:
        x = Alt_Odds(league, bet_type)
        self = x
        x.run()
