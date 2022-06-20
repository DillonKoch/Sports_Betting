# ==============================================================================
# File: run_models.py
# Project: allison
# File Created: Wednesday, 27th April 2022 7:47:59 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 27th April 2022 7:48:00 pm
# Modified By: Dillon Koch
# -----
#
# -----
# * running saved models on upcoming games, saving predictions in /Data/Predictions/
# ==============================================================================

import datetime
import os
import pickle
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
import torch
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


from train_models import (NeuralNet1, NeuralNet2, NeuralNet3, NeuralNet4,
                          NeuralNet5, NeuralNet6)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class Run_Models:
    def __init__(self, league, bet_type):
        self.league = league
        self.bet_type = bet_type

        self.neural_net_dict = {1: NeuralNet1, 2: NeuralNet2, 3: NeuralNet3, 4: NeuralNet4, 5: NeuralNet5, 6: NeuralNet6}
        self.modeling_df_dict = {i: self.load_modeling_df(i) for i in [3, 5, 10, 15, 20, 25]}

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

    def load_modeling_df(self, idx):  # Top Level __init__
        path = ROOT_PATH + f"/Data/Modeling_Data/{self.league}/player_stats_avg_{idx}_past_games.csv"
        df = pd.read_csv(path)
        return df

    def load_models(self):  # Top Level
        """
        loading models and their paths from /Models/
        """
        folder = ROOT_PATH + f"/Models/{self.league}/"
        model_paths = [item for item in listdir_fullpath(folder) if self.bet_type in item]
        models = []
        for model_path in model_paths:
            network_num = int(model_path.split('network')[1][0]) + 1
            model = self.neural_net_dict[network_num]().to('cuda')
            model.load_state_dict(torch.load(model_path))
            models.append(model)
        return models, model_paths

    def load_scalers(self, model_paths):  # Top Level
        """
        loading scalers used to create modeling_df to scale data the exact same way
        """
        scaler_folder = ROOT_PATH + f"/Modeling/scalers/{self.league}/"
        scaler_paths = sorted(listdir_fullpath(scaler_folder))
        scaler_dict = {}
        for apg, scaler_path in zip([3, 5, 10, 15, 20, 25], scaler_paths):
            with open(scaler_path, 'rb') as f:
                scaler = pickle.load(f)
            scaler_dict[apg] = scaler

        scalers = []
        for model_path in model_paths:
            path_apg = int(model_path.split('_')[-7])
            scalers.append(scaler_dict[path_apg])

        return scalers

    def load_pred_df(self):  # Top Level
        """
        loading predictions df or creating one if needed
        """
        path = ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv"
        if not os.path.exists(path):
            cols = ['Date', 'Home', 'Away', 'Bet_Type', 'Bet_Value', 'Bet_ML', 'Prediction', 'Outcome', "Pred_ts"]
            df = pd.DataFrame(columns=cols)
        else:
            df = pd.read_csv(path)
        return df

    def upcoming_games(self, df, scaler):  # Top Level
        """
        creating input X vectors for upcoming games
        """
        df['Date'] = pd.to_datetime(df['Date'])
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        yesterday = datetime.datetime(year=2022, month=4, day=15)
        df = df.loc[df['Date'] > yesterday]
        odds_cols = ['Home_Line_Close', 'Home_Line_Close_ML', 'OU_Close', 'OU_Close_ML', 'Home_ML', 'Away_ML']
        df = df.dropna(subset=odds_cols, axis=0)
        df.reset_index(drop=True, inplace=True)
        X_cols = [col for col in list(df.columns) if col not in (['Home', 'Away', "Date"] + self.all_target_cols)]
        X = np.array(df[X_cols])
        X = scaler.transform(X)
        X = torch.from_numpy(X).float().to('cuda')
        return df, X

    def _game_lists(self, pred_lists):  # Specific Helper update_pred_df
        """
        making lists of game info - date, home, away, bet_val, ..
        """
        game_lists = []
        for pred_list in pred_lists:
            added = False
            for game_list in game_lists:
                date_match = pred_list[0] == game_list[0][0]
                home_match = pred_list[1] == game_list[0][1]
                away_match = pred_list[2] == game_list[0][2]
                if date_match and home_match and away_match and (not added):
                    game_list.append(pred_list)
                    added = True
            if not added:
                game_lists.append([pred_list])
        return game_lists

    def update_pred_df(self, pred_df, pred_lists):  # Top Level
        """
        updating the predictions df with the models' outputs
        """
        game_lists = self._game_lists(pred_lists)
        for game_list in game_lists:
            avg_pred = sum([i[-1].item() for i in game_list]) / len(game_list)
            new_row = game_list[0][:-1] + [round(avg_pred, 3), "Not Labeled", self._current_ts()]
            pred_df.loc[len(pred_df)] = new_row

        pred_df.drop_duplicates(subset=['Date', 'Home', 'Away', 'Bet_Type'], keep="last", inplace=True)
        pred_df.to_csv(ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv", index=False)
        print("SAVED")

    def run(self):  # Run
        models, model_paths = self.load_models()
        scalers = self.load_scalers(model_paths)
        pred_df = self.load_pred_df()

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

        pred_df = self.update_pred_df(pred_df, pred_lists)


if __name__ == '__main__':
    league = "NBA"
    bet_type = "Total"
    x = Run_Models(league, bet_type)
    x.run()
