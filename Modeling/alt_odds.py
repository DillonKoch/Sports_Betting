# ==============================================================================
# File: alt_odds.py
# Project: allison
# File Created: Thursday, 28th April 2022 10:40:02 am
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 28th April 2022 10:40:02 am
# Modified By: Dillon Koch
# -----
#
# -----
# running models on alternate odds
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

    def load_alt_df(self):  # Top Level
        path = ROOT_PATH + f"/Data/Predictions/{self.league}/Alt_Predictions.csv"
        if not os.path.exists(path):
            cols = ['Date', 'Home', 'Away', 'Bet_Type', 'Bet_Value', 'Bet_ML', 'Prediction', 'Outcome', "Pred_ts"]
            df = pd.DataFrame(columns=cols)
        else:
            df = pd.read_csv(path)
        return df

    def _alt_odds(self, odds_val):   # Helping Helper _expand_df_alt_odds
        alt_odds = [odds_val - 5, odds_val - 4, odds_val - 3, odds_val - 2.5,
                    odds_val - 2, odds_val - 1.5, odds_val - 1, odds_val - 0.5,
                    odds_val, odds_val + 0.5, odds_val + 1, odds_val + 1.5,
                    odds_val + 2, odds_val + 2.5, odds_val + 3, odds_val + 4, odds_val + 5]
        if (0 not in alt_odds) and (self.bet_type == 'Spread'):
            alt_odds.append(0)
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

    def _game_lists(self, pred_lists):  # Specific Helper update_alt_df
        game_lists = []
        for pred_list in pred_lists:
            added = False
            for game_list in game_lists:
                date_match = pred_list[0] == game_list[0][0]
                home_match = pred_list[1] == game_list[0][1]
                away_match = pred_list[2] == game_list[0][2]
                bet_val_match = pred_list[4] == game_list[0][4]
                if date_match and home_match and away_match and bet_val_match and (not added):
                    game_list.append(pred_list)
                    added = True
            if not added:
                game_lists.append([pred_list])
        return game_lists

    def update_alt_df(self, alt_df, pred_lists):  # Top Level
        game_lists = self._game_lists(pred_lists)
        for game_list in game_lists:
            avg_pred = sum([i[-1].item() for i in game_list]) / len(game_list)
            new_row = game_list[0][:-1] + [round(avg_pred, 3), "Not Labeled", self._current_ts()]
            alt_df.loc[len(alt_df)] = new_row

        alt_df.drop_duplicates(subset=['Date', 'Home', 'Away', 'Bet_Type', 'Bet_Value', 'Bet_ML'], keep="last", inplace=True)
        alt_df.to_csv(ROOT_PATH + f"/Data/Predictions/{self.league}/Alt_Predictions.csv", index=False)
        print("SAVED")

    def run(self):  # Run
        models, model_paths = self.load_models()
        scalers = self.load_scalers(model_paths)
        alt_df = self.load_alt_df()

        pred_lists = []
        for model, model_path, scaler in tqdm(zip(models, model_paths, scalers)):
            modeling_df = self.modeling_df_dict[int(model_path.split('_')[-7])]
            modeling_df, X = self.upcoming_games(modeling_df, scaler)
            for i in range(len(modeling_df)):
                pred = model(X[i])
                date = str(modeling_df.iloc[i]['Date']).split(" ")[0]
                home = modeling_df.iloc[i]['Home']
                away = modeling_df.iloc[i]['Away']
                bet_value = modeling_df.iloc[i][self.bet_val_dict[self.bet_type]]
                bet_ml = modeling_df.iloc[i][self.bet_val_ml_dict[self.bet_type]]
                pred_list = [date, home, away, self.bet_type, bet_value, bet_ml, pred]
                pred_lists.append(pred_list)

        # pred_df = self.update_pred_df(pred_df, pred_lists)
        alt_df = self.update_alt_df(alt_df, pred_lists)


if __name__ == '__main__':
    league = "NBA"
    bet_type = "Total"
    x = Alt_Odds(league, bet_type)
    self = x
    x.run()
