# ==============================================================================
# File: train_models.py
# Project: allison
# File Created: Sunday, 24th April 2022 6:20:34 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 24th April 2022 6:20:40 pm
# Modified By: Dillon Koch
# -----
#
# -----
# training
# ==============================================================================


import copy
import datetime
import os
import pickle
import random
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import wandb
from sklearn.preprocessing import StandardScaler
from torch import nn
from torch.utils.data import DataLoader, Dataset

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class SBDataset(Dataset):
    def __init__(self, league, train_val_test, bet_type, player_stats, avg_past_games):
        super(SBDataset, self).__init__()
        self.league = league
        self.train_val_test = train_val_test
        self.bet_type = bet_type
        self.player_stats = player_stats
        self.avg_past_games = avg_past_games

        # * identifying target column
        self.bet_type_to_target_col = {"Spread": "Home_Covered", "Moneyline": "Home_Win",
                                       "Total": "Over_Covered"}
        self.target_col = self.bet_type_to_target_col[self.bet_type]
        self.all_target_cols = list(self.bet_type_to_target_col.values())

        # * loading X/y data
        df = self.finished_games()
        train_df, val_df, test_df = self.train_val_test_split(df)
        train_df = self.balance_classes(train_df)
        val_df = self.balance_classes(val_df)
        test_df = self.balance_classes(test_df)
        self.X, self.y = self.scaled_xy(train_df, val_df, test_df, train_val_test)

    def _load_df(self):  # Specific Helper
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

    def finished_games(self):  # Top Level
        """
        loading the /Data/Modeling_Data/ df of finished games only
        """
        raw_df = self._load_df()
        raw_df['Date'] = pd.to_datetime(raw_df['Date'])
        yesterday = datetime.datetime.today() - datetime.timedelta(days=1)
        finished_df = raw_df.loc[raw_df['Date'] < yesterday]
        finished_df = self._remove_missing_odds_cols(finished_df)
        return finished_df

    def _past_recent_split(self, df):  # Specific Helper train_test_split
        """
        making lists of indices in the dataframe that belong to "past" and "recent"
        """
        past_idx = []
        recent_idx = []
        for i, row in df.iterrows():
            if row['Date'].year < 2018:
                past_idx.append(i)
            else:
                recent_idx.append(i)

        random.shuffle(past_idx)
        random.shuffle(recent_idx)
        return past_idx, recent_idx

    def _split_idx_list(self, idx_list, train_pct, val_pct):
        """
        splitting a given idx_list into train/val/test lists
        """
        split1 = int(len(idx_list) * train_pct)
        split2 = int(len(idx_list) * (train_pct + val_pct))
        train_idx = idx_list[:split1]
        val_idx = idx_list[split1:split2]
        test_idx = idx_list[split2:]
        return train_idx, val_idx, test_idx

    def _idx_lists_to_df(self, df, past_idx, recent_idx):  # Specific Helper train_test_split
        """
        subsetting the df to only rows in the past_idx or recent_idx lists
        """
        all_idx = past_idx + recent_idx
        df_copy = copy.deepcopy(df)
        filtered_df = df_copy.loc[df_copy.index.isin(all_idx)]
        filtered_df.reset_index(inplace=True, drop=True)
        return filtered_df

    def train_val_test_split(self, df):  # Top Level
        """
        splitting the data into train/val/test groups
        """
        past_idx, recent_idx = self._past_recent_split(df)
        past_train_idx, past_val_idx, past_test_idx = self._split_idx_list(past_idx, train_pct=.9, val_pct=.05)
        recent_train_idx, recent_val_idx, recent_test_idx = self._split_idx_list(recent_idx, train_pct=.4, val_pct=.3)
        train_df = self._idx_lists_to_df(df, past_train_idx, recent_train_idx)
        val_df = self._idx_lists_to_df(df, past_val_idx, recent_val_idx)
        test_df = self._idx_lists_to_df(df, past_test_idx, recent_test_idx)
        return train_df, val_df, test_df

    def balance_classes(self, df):  # Top Level
        """
        resampling the lesser-represented class to balance the dataset
        """
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

    def scaled_xy(self, train_df, val_df, test_df, train_val_test):  # Top Level
        """
        scaling the data and separating into X/y tensors
        """
        # * fitting the scaler on the train set regardless of train_data
        train_y = np.array(train_df[self.target_col])
        X_cols = [col for col in list(train_df.columns) if col not in (['Home', "Away", "Date"] + self.all_target_cols)]
        train_X = np.array(train_df[X_cols])
        scaler = StandardScaler()
        train_X = scaler.fit_transform(train_X)

        # * choosing X/y based on whether we want train/test data
        if train_val_test == "train":
            X = train_X
            y = train_y
        elif train_val_test == "val":
            y = np.array(val_df[self.target_col])
            X = np.array(val_df[X_cols])
            X = scaler.transform(X)
        elif train_val_test == "test":
            y = np.array(test_df[self.target_col])
            X = np.array(test_df[X_cols])
            X = scaler.transform(X)

        X = torch.from_numpy(X).float().to('cuda')
        y = torch.from_numpy(y).float().to('cuda')
        self._save_scaler(scaler)
        return X, y

    def __len__(self):  # Run
        """
        returns the number of items in the dataset
        """
        return self.y.shape[0]

    def __getitem__(self, idx):  # Run
        """
        returns one (X, y) pair at index "idx"
        """
        return self.X[idx], self.y[idx]


class NeuralNet1(nn.Module):
    def __init__(self):
        super(NeuralNet1, self).__init__()
        self.fc1 = nn.Linear(542, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):  # Run
        """
        returns the output of the network for a single input x
        """
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = self.sigmoid(self.fc4(x))
        return x


class NeuralNet2(nn.Module):
    def __init__(self):
        super(NeuralNet2, self).__init__()
        self.fc1 = nn.Linear(542, 384)
        self.fc2 = nn.Linear(384, 256)
        self.fc3 = nn.Linear(256, 128)
        self.fc4 = nn.Linear(128, 64)
        self.fc5 = nn.Linear(64, 32)
        self.fc6 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):  # Run
        """
        returns the output of the network for a single input x
        """
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = F.relu(self.fc5(x))
        x = self.sigmoid(self.fc6(x))
        return x


class NeuralNet3(nn.Module):
    def __init__(self):
        super(NeuralNet3, self).__init__()
        self.fc1 = nn.Linear(542, 256)
        self.fc2 = nn.Linear(256, 128)
        self.fc3 = nn.Linear(128, 64)
        self.fc4 = nn.Linear(64, 1)
        self.sigmoid = nn.Sigmoid()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):  # Run
        """
        returns the output of the network for a single input x
        """
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.relu(self.fc3(x))
        x = self.sigmoid(self.fc4(x))
        return x


class NeuralNet4(nn.Module):
    def __init__(self):
        super(NeuralNet4, self).__init__()
        self.fc1 = nn.Linear(542, 384)
        self.fc2 = nn.Linear(384, 256)
        self.fc3 = nn.Linear(256, 128)
        self.fc4 = nn.Linear(128, 64)
        self.fc5 = nn.Linear(64, 32)
        self.fc6 = nn.Linear(32, 1)
        self.sigmoid = nn.Sigmoid()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):  # Run
        """
        returns the output of the network for a single input x
        """
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.relu(self.fc3(x))
        x = self.dropout(x)
        x = F.relu(self.fc4(x))
        x = self.dropout(x)
        x = F.relu(self.fc5(x))
        x = self.sigmoid(self.fc6(x))
        return x


class NeuralNet5(nn.Module):
    def __init__(self):
        super(NeuralNet5, self).__init__()
        self.fc1 = nn.Linear(542, 500)
        self.fc2 = nn.Linear(500, 450)
        self.fc3 = nn.Linear(450, 400)
        self.fc4 = nn.Linear(400, 350)
        self.fc5 = nn.Linear(350, 300)
        self.fc6 = nn.Linear(300, 250)
        self.fc7 = nn.Linear(250, 200)
        self.fc8 = nn.Linear(200, 150)
        self.fc9 = nn.Linear(150, 100)
        self.fc10 = nn.Linear(100, 50)
        self.fc11 = nn.Linear(50, 1)
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):  # Run
        """
        returns the output of the network for a single input x
        """
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = F.relu(self.fc3(x))
        x = F.relu(self.fc4(x))
        x = F.relu(self.fc5(x))
        x = F.relu(self.fc6(x))
        x = F.relu(self.fc7(x))
        x = F.relu(self.fc8(x))
        x = F.relu(self.fc9(x))
        x = F.relu(self.fc10(x))
        x = self.sigmoid(self.fc11(x))
        return x


class NeuralNet6(nn.Module):
    def __init__(self):
        super(NeuralNet6, self).__init__()
        self.fc1 = nn.Linear(542, 500)
        self.fc2 = nn.Linear(500, 450)
        self.fc3 = nn.Linear(450, 400)
        self.fc4 = nn.Linear(400, 350)
        self.fc5 = nn.Linear(350, 300)
        self.fc6 = nn.Linear(300, 250)
        self.fc7 = nn.Linear(250, 200)
        self.fc8 = nn.Linear(200, 150)
        self.fc9 = nn.Linear(150, 100)
        self.fc10 = nn.Linear(100, 50)
        self.fc11 = nn.Linear(50, 1)
        self.sigmoid = nn.Sigmoid()
        self.dropout = nn.Dropout(0.5)

    def forward(self, x):  # Run
        """
        returns the output of the network for a single input x
        """
        x = F.relu(self.fc1(x))
        x = self.dropout(x)
        x = F.relu(self.fc2(x))
        x = self.dropout(x)
        x = F.relu(self.fc3(x))
        x = self.dropout(x)
        x = F.relu(self.fc4(x))
        x = self.dropout(x)
        x = F.relu(self.fc5(x))
        x = self.dropout(x)
        x = F.relu(self.fc6(x))
        x = self.dropout(x)
        x = F.relu(self.fc7(x))
        x = self.dropout(x)
        x = F.relu(self.fc8(x))
        x = self.dropout(x)
        x = F.relu(self.fc9(x))
        x = self.dropout(x)
        x = F.relu(self.fc10(x))
        x = self.sigmoid(self.fc11(x))
        return x


class TrainNetwork:
    def __init__(self, league, bet_type, avg_past_games, batch_size, epochs, learning_rate, momentum, network_idx, optimizer, wandb_sweep=False, wandb_single=False):
        # * sports betting params
        self.league = league
        self.bet_type = bet_type
        self.avg_past_games = avg_past_games

        # * hyperparameters
        self.batch_size = batch_size
        self.epochs = epochs
        self.learning_rate = learning_rate
        self.momentum = momentum

        # * weights and biases
        self.wandb_sweep = wandb_sweep
        self.wandb_single = wandb_single
        self.wandb = wandb_sweep or wandb_single
        if self.wandb_single:
            wandb.init(project="Sports_Betting", entity="dillonkoch", reinit=True)
            wandb.config = {"epochs": self.epochs, "batch_size": self.batch_size, "learning_rate": self.learning_rate, "momentum": self.momentum}

        # * train/val/test dataloaders
        self.train_dataset = SBDataset(league, "train", bet_type, True, avg_past_games)
        self.train_dataloader = DataLoader(self.train_dataset, batch_size=self.batch_size, shuffle=True)

        self.val_dataset = SBDataset(league, "val", bet_type, True, avg_past_games)
        self.val_dataloader = DataLoader(self.val_dataset, batch_size=self.batch_size, shuffle=True)

        self.test_dataset = SBDataset(league, "test", bet_type, True, avg_past_games)
        self.test_dataloader = DataLoader(self.test_dataset, batch_size=self.batch_size, shuffle=True)

        # * model
        self.network_idx = network_idx
        self.models = [NeuralNet1, NeuralNet2, NeuralNet3, NeuralNet4, NeuralNet5, NeuralNet6]
        self.model = self.models[network_idx]().to("cuda")
        self.loss = nn.BCELoss()
        self.optimizer_name = optimizer
        self.optimizer = self.get_optimizer(optimizer)

    def get_optimizer(self, opt_name):  # Top Level
        """
        creating the specified optimizer
        """
        if opt_name == 'adam':
            return torch.optim.Adam(self.model.parameters(), lr=self.learning_rate)
        elif opt_name == 'sgd':
            return torch.optim.SGD(self.model.parameters(), lr=self.learning_rate, momentum=self.momentum)
        elif opt_name == 'rmsprop':
            return torch.optim.RMSprop(self.model.parameters(), lr=self.learning_rate)

    def train_loop(self):  # Top Level
        """
        running and updating the neural net on the training data
        """
        self.model.train()

        for batch_idx, (X, y) in enumerate(self.train_dataloader):
            self.optimizer.zero_grad()

            pred = self.model(X)
            loss = self.loss(pred, torch.unsqueeze(y, 1))
            loss.backward()
            self.optimizer.step()

            if self.wandb:
                wandb.log({"Training Loss": loss.item()})

            if batch_idx % 100 == 0:
                print(f"Batch {batch_idx+1}/{len(self.train_dataloader)}: Loss: {loss.item()}")

    def val_loop(self):  # Top Level
        """
        evaluating the neural net's predictions on the validation set
        """
        self.model.eval()
        val_loss = 0
        correct = 0

        with torch.no_grad():
            for X, y in self.val_dataloader:
                output = self.model(X)
                val_loss += self.loss(output, torch.unsqueeze(y, 1))
                pred = torch.round(output)
                correct += pred.eq(y.view_as(pred)).sum().item()

        val_loss /= len(self.val_dataloader.dataset)

        print(f"\nVal set: Average loss: {val_loss:.4f}, Accuracy: {correct / len(self.val_dataloader.dataset):.4f}%")
        if self.wandb:
            wandb.log({"Val Loss": val_loss, "Val Accuracy": correct / len(self.val_dataloader.dataset)})

        return val_loss.item()

    def test_loop(self):  # Top Level
        """
        evaluating the neural net's predictions on the test set
        """
        self.model.eval()
        test_loss = 0
        correct = 0

        with torch.no_grad():
            for X, y in self.test_dataloader:
                output = self.model(X)
                test_loss += self.loss(output, torch.unsqueeze(y, 1))
                pred = torch.round(output)
                correct += pred.eq(y.view_as(pred)).sum().item()

        test_loss /= len(self.test_dataloader.dataset)

        print(f"\nTest set: Average loss: {test_loss:.4f}, Accuracy: {correct / len(self.test_dataloader.dataset):.4f}%")
        if self.wandb:
            wandb.log({"Test Loss": test_loss, "Test Accuracy": correct / len(self.test_dataloader.dataset)})

        return test_loss.item()

    def update_sweep_csv(self, min_loss):  # Top Level
        """
        updates the sweep csv with the current model's hyperparameters and loss
        - creates the sweep csv if necessary
        """
        sweep_csv_path = ROOT_PATH + f"/Modeling/Sweeps/{self.league}_{self.bet_type}_sweep.csv"
        if not os.path.exists(sweep_csv_path):
            cols = ['Date', 'avg_past_games', 'batch_size', 'learning_rate', 'momentum', 'optimizer', 'network_idx', 'epochs', 'loss']
            df = pd.DataFrame(columns=cols)
        else:
            df = pd.read_csv(sweep_csv_path)

        today_str = datetime.datetime.today().strftime("%Y-%m-%d")
        new_row = [today_str, self.avg_past_games, self.batch_size, self.learning_rate, self.momentum, self.optimizer_name, self.network_idx, self.epochs, min_loss]
        df.loc[len(df)] = new_row
        df.to_csv(sweep_csv_path, index=False)
        print("SAVED SWEEP CSV")

    def _clear_others(self, model_path):  # Specific Helper  save_model
        """
        clearing out models with the same setup that performed worse than the new best
        """
        path_start = model_path.split("loss")[0]
        folder = ROOT_PATH + f"/Models/{self.league}/"
        for path in listdir_fullpath(folder):
            if path.startswith(path_start):
                os.remove(path)

    def save_model(self, min_loss, loss):  # Top Level
        """
        saving the model to disk if it's the best one so far
        """
        if loss < min_loss:
            lr_str = str(self.learning_rate).split('.')[1][:5]
            loss_str = str(loss).split(".")[1][:5]
            model_path = ROOT_PATH + f"/Models/{self.league}/{self.bet_type}_{self.avg_past_games}_apg_network{self.network_idx}_lr_{lr_str}_loss_{loss_str}.pth"
            self._clear_others(model_path)
            torch.save(self.model.state_dict(), model_path)

    def train(self, val=True, early_stopping=10000, sweep_csv=False, save_model=False):  # Run
        min_loss = float('inf')
        loss_inc_count = 0

        # * running train and val/test loop to start each epoch
        for i in range(self.epochs):
            print(f"Epoch {i+1}")
            self.train_loop()
            loss = self.val_loop() if val else self.test_loop()
            if save_model:
                self.save_model(min_loss, loss)

            # * updating min_loss/loss_inc_count and stopping early if necessary
            loss_inc_count = 0 if loss < min_loss else loss_inc_count + 1
            min_loss = min(min_loss, loss)
            if (loss_inc_count > early_stopping):
                print("Early stopping")
                break

        if sweep_csv:
            self.update_sweep_csv(min_loss)


class Main:
    def __init__(self, league, bet_type):
        self.league = league
        self.bet_type = bet_type

    def train_single(self):  # Run
        """
        just training one model, wandb optional
        - used just for testing something out
        """
        # ! Parameters to update
        wandb_single = True
        avg_past_games = 10
        batch_size = 256
        epochs = 100
        learning_rate = 0.001
        momentum = 0.9
        network_idx = 5
        optimizer = 'adam'
        trainer = TrainNetwork(self.league, self.bet_type, avg_past_games, batch_size, epochs, learning_rate, momentum, network_idx, optimizer, wandb_single=wandb_single)
        trainer.train(val=True, early_stopping=20, sweep_csv=False)

    def sweep(self):  # Run
        """
        runs a wandb sweep with different hyperparameters, evaluated on validation set
        - used to determine best hyperparameters, saves them to csv
        """
        def train_wandb(config=None):
            with wandb.init(config=config):
                config = wandb.config
                epochs = 100
                trainer = TrainNetwork(
                    league,
                    bet_type,
                    config.avg_past_games,
                    config.batch_size,
                    epochs,
                    config.learning_rate,
                    config.momentum,
                    config.network_idx,
                    config.optimizer,
                    wandb_sweep=True)
                trainer.train(val=True, early_stopping=30, sweep_csv=True)

        sweep_id = "dillonkoch/Sports_Betting/esv5es4l"
        wandb.agent(sweep_id, train_wandb, count=1000)

    def load_best_hyperparameters(self):  # Top Level
        df_path = ROOT_PATH + f"/Modeling/Sweeps/{self.league}_{self.bet_type}_sweep.csv"
        df = pd.read_csv(df_path)
        row_dicts = df.to_dict('records')
        params = sorted(row_dicts, key=lambda x: x['loss'])[:10]
        return params

    def train_best_on_test(self, wandb=True, n=10):  # Run
        """
        loads n best hyperparameter settings from csv, trains them on test data
        - run this after a sweep to get the best models trained and saved
        """
        params = self.load_best_hyperparameters()
        for param in params:
            def run_param(param):
                apg = param['avg_past_games']
                batch_size = param['batch_size']
                learning_rate = param['learning_rate']
                momentum = param['momentum']
                optimizer = param['optimizer']
                network_idx = param['network_idx']

                trainer = TrainNetwork(self.league, self.bet_type, apg, batch_size, 100, learning_rate, momentum, network_idx, optimizer, wandb_single=wandb)
                trainer.train(val=False, early_stopping=40, save_model=True)

            run_param(param)


if __name__ == "__main__":
    # ! SETUP
    league = "NBA"
    bet_type = "Total"
    x = Main(league, bet_type)

    # ! RUNNING
    # x.train_single()
    # x.sweep()
    x.train_best_on_test()
