# ==============================================================================
# File: train_models.py
# Project: allison
# File Created: Thursday, 7th April 2022 5:25:35 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 7th April 2022 5:25:36 pm
# Modified By: Dillon Koch
# -----
#
# -----
# processing data into X/y vectors (datloaders)
# training models and saving the best ones (model class)
# ==============================================================================


import datetime
import os
import pickle
import shutil
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, Dataset

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class SBDataset(Dataset):
    def __init__(self, league, bet_type, player_stats, avg_past_games):
        self.league = league
        self.bet_type = bet_type
        self.player_stats = player_stats
        self.avg_past_games = avg_past_games

        # * identifying target column
        self.bet_type_to_target_col = {"Spread": "Home_Covered", "Moneyline": "Home_Win",
                                       "Total": "Over_Covered"}
        self.target_col = self.bet_type_to_target_col[self.bet_type]
        self.all_target_cols = list(self.bet_type_to_target_col.values())

        # * loading data
        df = self.finished_games()
        df = self.balance_classes(df)
        self.X, self.y = self.scaled_xy(df)

    def _load_df(self):  # Specific Helper finished_games
        """
        loading the dataset from /Data/Modeling_Data/ for the league, player stats, avg past games
        """
        player_stat_str = "player_stats" if self.player_stats else "no_player_stats"
        path = ROOT_PATH + f"/Data/Modeling_Data/{self.league}/{player_stat_str}_avg_{self.avg_past_games}_past_games.csv"
        df = pd.read_csv(path)
        return df

    def _remove_missing_odds_cols(self, df):  # Specific Helper finished_games
        """
        sometimes betting odds won't be available for some recent games, so taking those out
        """
        cols = ['Home_Line_Close', 'Home_Line_Close_ML', 'OU_Close', 'OU_Close_ML', 'Home_ML', 'Away_ML']
        df = df.dropna(subset=cols, axis=0)
        assert df.isnull().sum().sum() == 0
        return df

    def finished_games(self):  # Top Level __init__
        """
        loading the /Data/Modeling_Data/ df of finished games only
        """
        raw_df = self._load_df()
        raw_df['Date'] = pd.to_datetime(raw_df['Date'])
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        finished_df = raw_df.loc[raw_df['Date'] < yesterday]
        finished_df = self._remove_missing_odds_cols(finished_df)
        return finished_df

    def balance_classes(self, df):  # Top Level __init__
        """
        resampling the lesser-represented class to balance the dataset
        """
        # TODO make a 0.5 for push in Modeling_Data labels

        # * separating the dataset into those with positive/negative labels
        positives = df[df[self.target_col] == 1]
        positives.reset_index(drop=True, inplace=True)
        negatives = df[df[self.target_col] == 0]

        # * determining which is undersampled, and resampling latest games to make it even
        if len(positives) > len(negatives):
            diff = len(positives) - len(negatives)
            negatives = pd.concat([negatives, negatives.iloc[-diff:, :]])
        else:
            diff = len(negatives) - len(positives)
            positives = pd.concat([positives, positives.iloc[-diff:, :]])

        # * adding the two halves of the dataset back together
        balanced_df = pd.concat([positives, negatives])
        return balanced_df

    def _save_scaler(self, scaler):  # Specific Helper scaled_xy
        """
        saving the scaler to a pickle file so run_models.py can use the same one
        """
        path = ROOT_PATH + f"/Modeling/scalers/{self.league}/avg_{self.avg_past_games}_past_games_scaler.pkl"
        with open(path, 'wb') as f:
            pickle.dump(scaler, f)

    def scaled_xy(self, df):  # Top Level __init__
        """
        scaling the data and separating into X/y tensors
        """
        y = np.array(df[self.target_col])
        X_cols = [col for col in list(df.columns) if col not in (['Home', "Away", "Date"] + self.all_target_cols)]
        X = np.array(df[X_cols])
        scaler = StandardScaler()
        X = scaler.fit_transform(X)
        X = torch.from_numpy(X).float().to('cuda')
        y = torch.from_numpy(y).float().to('cuda')
        self._save_scaler(scaler)
        return X, y

    def __len__(self):  # Run
        return self.y.shape[0]

    def __getitem__(self, idx):  # Run
        return self.X[idx], self.y[idx]


class SBModel(nn.Module):
    def __init__(self):
        super(SBModel, self).__init__()
        self.fc1 = nn.Linear(542, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.sigmoid(self.fc4(x))
        return x


class Train:
    def __init__(self, league, bet_type):
        self.league = league
        self.bet_type = bet_type
        self.temp_model_path = ROOT_PATH + f"/Models/{self.league}/{self.bet_type}_temp_model.pth"

        # * model
        self.loss_fn = nn.BCELoss()
        # self.optimizer = torch.optim.Adam(self.model.parameters(), lr=0.001)
        self.epochs = 10

    def train_loop(self, model, train_dataloader, optimizer):  # Top Level
        size = len(train_dataloader)
        for batch, (X, y) in enumerate(train_dataloader):
            pred = model(X)
            loss = self.loss_fn(pred, torch.unsqueeze(y, 1))

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            # print(f"Loss: {loss:.7f} | Batch: {batch}/{size}")

    def test_loop(self, model, test_dataloader):  # Top Level
        num_batches = len(test_dataloader)
        test_loss = 0
        correct = 0
        total = 0

        with torch.no_grad():
            for batch, (X, y) in enumerate(test_dataloader):
                pred = model(X)
                loss = self.loss_fn(pred, torch.unsqueeze(y, 1))
                test_loss += loss.item()
                # print(f"Loss: {loss:.7f} | Batch: {batch}/{num_batches}")

                # * accuracy
                binary_preds = torch.reshape(pred > 0.5, (-1,)).int()
                correct += torch.sum(binary_preds == y).item()
                total += y.shape[0]

        print(f"Accuracy: {(correct / total):.3f}%")
        return test_loss / num_batches

    def train_one(self, dataset, model, optimizer):  # Run
        train_size = int(0.8 * len(dataset))
        test_size = len(dataset) - train_size
        train_dataset, test_dataset = torch.utils.data.random_split(dataset, [train_size, test_size])
        train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)
        test_dataloader = DataLoader(test_dataset, batch_size=32, shuffle=True)

        min_loss = float('inf')
        for i in range(self.epochs):
            self.train_loop(model, train_dataloader, optimizer)
            test_loss = self.test_loop(model, test_dataloader)
            print(f"{test_loss:.4f}")
            if test_loss < min_loss:
                min_loss = test_loss
                torch.save(model.state_dict(), self.temp_model_path)

        return min_loss, model

    def save_model(self, model, avg_past_games):   # Top Level train_all
        # * copy the temp model over to the path we want
        model_path = ROOT_PATH + f"/Models/{self.league}/{self.bet_type}_{avg_past_games}_avg_past_games_model.pth"
        shutil.copyfile(self.temp_model_path, model_path)
        print("Saved new best model!")

        # * delete other models
        paths = listdir_fullpath(ROOT_PATH + f"/Models/{self.league}/")
        paths.remove(model_path)
        bet_type_paths = [path for path in paths if self.bet_type in path]
        for path in bet_type_paths:
            os.remove(path)

    def delete_temps(self):  # Top Level
        paths = listdir_fullpath(ROOT_PATH + f"/Models/{self.league}/")
        temps = [path for path in paths if 'temp' in path]
        for temp in temps:
            os.remove(temp)

    def train_all(self):  # Run
        min_test_loss = float('inf')
        for player_stats in [True]:
            for avg_past_games in [3, 5, 10, 15, 20, 25]:
                dataset = SBDataset(self.league, self.bet_type, player_stats, avg_past_games)
                model = SBModel().to('cuda')
                optimizer = torch.optim.Adam(model.parameters(), lr=0.001)
                current_min_test_loss, model = self.train_one(dataset, model, optimizer)
                print(f"Player stats: {player_stats}, Avg past games: {avg_past_games}, min test loss: {current_min_test_loss}")

                # * if the current model has the lowest loss, save it
                if current_min_test_loss < min_test_loss:
                    # torch.save(model.state_dict(), self.model_path)
                    # ! load temp weights, save to real path
                    self.save_model(model, avg_past_games)
                    # model_path = ROOT_PATH + f"/Models/{self.league}/{self.bet_type}_{avg_past_games}_avg_past_games_model.pth"
                    # shutil.copyfile(self.temp_model_path, model_path)
                    min_test_loss = current_min_test_loss
                    # print("Saved new best model!")

        self.delete_temps()


if __name__ == '__main__':
    league = "NBA"
    for bet_type in ['Spread', 'Total']:
        # bet_type = "Spread"
        x = Train(league, bet_type)
        self = x
        x.train_all()
