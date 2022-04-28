# ==============================================================================
# File: run_models.py
# Project: allison
# File Created: Thursday, 7th April 2022 5:26:27 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 7th April 2022 5:26:55 pm
# Modified By: Dillon Koch
# -----
#
# -----
# running the saved models on upcoming games and saving predictions
# ==============================================================================

import datetime
import os
import sys
from os.path import abspath, dirname

import numpy as np
import pickle
import pandas as pd
import torch

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from train_models import SBModel


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class Run_Models:
    def __init__(self, league, bet_type):
        self.league = league
        self.bet_type = bet_type

        # * identifying target column
        self.bet_type_to_target_col = {"Spread": "Home_Covered", "Moneyline": "Home_Win",
                                       "Total": "Over_Covered"}
        self.target_col = self.bet_type_to_target_col[self.bet_type]
        self.all_target_cols = list(self.bet_type_to_target_col.values())

        # * bet value dicts
        self.bet_val_dict = {"Spread": "Home_Line_Close", "Total": "OU_Close"}
        self.bet_val_ml_dict = {"Spread": "Home_Line_Close_ML", "Total": "OU_Close_ML"}

    def _current_ts(self):  # Global Helper
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def load_model(self):  # Top Level
        """
        loading the best saved model from /Models/{self.league}/ for the bet type
        """
        paths = listdir_fullpath(ROOT_PATH + f"/Models/{self.league}/")
        bet_type_paths = [path for path in paths if self.bet_type in path]
        assert len(bet_type_paths) == 1
        model_path = bet_type_paths[0]
        model = SBModel().to('cuda')
        model.load_state_dict(torch.load(model_path))
        return model, model_path

    def load_modeling_df(self, model_path):  # Top Level
        """
        loading the appropriate modeling_df based on which model was saved as best
        - # avg past games and player stats may vary
        """
        avg_past_games = model_path.split("/")[-1].split("_")[1]
        df_path = ROOT_PATH + f"/Data/Modeling_Data/{self.league}/player_stats_avg_{avg_past_games}_past_games.csv"
        df = pd.read_csv(df_path)
        return df

    def load_scaler(self, model_path):  # Top Level
        avg_past_games = model_path.split("/")[-1].split("_")[1]
        scaler_path = ROOT_PATH + f"/Modeling/scalers/{self.league}/avg_{avg_past_games}_past_games_scaler.pkl"
        with open(scaler_path, 'rb') as f:
            scaler = pickle.load(f)
        return scaler

    def upcoming_games(self, df, scaler):  # Top Level
        """
        creating input X vectors for upcoming games
        """
        df['Date'] = pd.to_datetime(df['Date'])
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        df = df.loc[df['Date'] > yesterday]
        odds_cols = ['Home_Line_Close', 'Home_Line_Close_ML', 'OU_Close', 'OU_Close_ML', 'Home_ML', 'Away_ML']
        df = df.dropna(subset=odds_cols, axis=0)
        df.reset_index(drop=True, inplace=True)
        X_cols = [col for col in list(df.columns) if col not in (['Home', 'Away', "Date"] + self.all_target_cols)]
        X = np.array(df[X_cols])
        X = scaler.transform(X)
        X = torch.from_numpy(X).float().to('cuda')
        return df, X

    def load_pred_df(self):  # Top Level
        path = ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv"
        if not os.path.exists(path):
            cols = ['Date', 'Home', 'Away', 'Bet_Type', 'Bet_Value', 'Bet_ML', 'Prediction', 'Outcome', "Pred_ts"]
            df = pd.DataFrame(columns=cols)
        else:
            df = pd.read_csv(path)
        return df

    def update_pred_df(self, pred_df, pred, modeling_df):  # Top Level
        """
        updating the pred_df in /Data/Predictions/{self.league}/Predictions.csv with new predictions
        """
        date = modeling_df['Date'].strftime('%Y-%m-%d')
        home = modeling_df['Home']
        away = modeling_df['Away']
        bet_val = modeling_df[self.bet_val_dict[self.bet_type]]
        bet_val_ml = modeling_df[self.bet_val_ml_dict[self.bet_type]]
        pred = round(pred.item(), 3)
        new_row = [date, home, away, self.bet_type, bet_val, bet_val_ml, pred, "Not Labeled", self._current_ts()]
        pred_df.loc[len(pred_df)] = new_row
        return pred_df

    def run(self):  # Run
        model, model_path = self.load_model()
        modeling_df = self.load_modeling_df(model_path)
        scaler = self.load_scaler(model_path)
        modeling_df, X = self.upcoming_games(modeling_df, scaler)
        pred_df = self.load_pred_df()
        for i in range(len(modeling_df)):
            print(len(pred_df))
            current_X = X[i]
            pred = model(current_X)
            pred_df = self.update_pred_df(pred_df, pred, modeling_df.iloc[i, :])
        pred_df.drop_duplicates(subset=['Date', 'Home', 'Away', 'Bet_Type'], keep="last", inplace=True)
        pred_df.to_csv(ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv", index=False)


if __name__ == '__main__':
    league = 'NBA'
    # bet_type = 'Total'
    for bet_type in ['Spread', 'Total']:
        x = Run_Models(league, bet_type)
        self = x
        x.run()
