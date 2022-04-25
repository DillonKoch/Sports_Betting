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


import os
import sys
from os.path import abspath, dirname

import wandb
import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset
from torchvision.io import read_image

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


class CustomDataset(Dataset):
    def __init__(self, train_data):
        super(CustomDataset, self).__init__()
        self.train_data = train_data
        # TODO load data or paths to images
        # TODO optional: data augmentation
        # TODO optional: define transforms

    def __len__(self):  # Run
        """
        returns the number of items in the dataset
        """
        pass

    def __getitem__(self, idx):  # Run
        """
        returns one (X, y) pair at index "idx"
        """
        # TODO set device to cuda for both X, y
        # TODO preprocess data (subtract mean, zero-centering)
        img_path = self.img_paths[idx]
        img = read_image(img_path).to('cuda') / 255.0
        img = self.transform(img)
        label = torch.tensor(self.labels[idx]).to('cuda')
        return img, label


# ! Create multiple Neural Net classes if desired
class NeuralNet1(nn.Module):
    def __init__(self):
        super(NeuralNet1, self).__init__()
        # TODO define layers

    def forward(self, x):  # Run
        """
        returns the output of the network for a single input x
        """
        # TODO define network architecture
        pass


class NeuralNet2(nn.Module):
    def __init__(self):
        super(NeuralNet2, self).__init__()
        # TODO define layers

    def forward(self, x):  # Run
        """
        returns the output of the network for a single input x
        """
        # TODO define network architecture
        pass


class TrainNetwork:
    def __init__(self, batch_size, epochs, learning_rate, momentum, network_idx, optimizer, wandb_sweep=False, wandb_single=False):
        # * hyperparameters
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.momentum = momentum

        # * weights and biases
        self.wandb_sweep = wandb_sweep
        self.wandb_single = wandb_single
        self.wandb = wandb_sweep or wandb_single
        if self.wandb_single:
            wandb.init(project="Fundamentals", entity="dillonkoch")
            wandb.config = {"epochs": self.epochs, "batch_size": self.batch_size, "learning_rate": self.learning_rate, "momentum": self.momentum}

        # TODO define train/test dataloaders
        # * optional: weighted random sampler for unequal class sizes
        self.train_dataset = CustomDataset("Train")
        self.train_dataloader = DataLoader(self.train_dataset, batch_size=self.batch_size)

        self.test_dataset = CustomDataset("Test")
        self.test_dataloader = DataLoader(self.test_dataset, batch_size=self.batch_size)

        # TODO define model
        # self.model = NeuralNet().to("cuda")
        self.models = [NeuralNet1, NeuralNet2]
        self.model = self.models[network_idx]().to("cuda")
        self.loss = nn.CrossEntropyLoss()
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

    def clear_temp(self):  # Top Level
        """
        clearing out the temp folder for a new run
        """
        temp_folder = ROOT_PATH + "/temp"
        for file in listdir_fullpath(temp_folder):
            os.remove(file)

    def train_loop(self):  # Top Level
        self.model.train()

        for batch_idx, (X, y) in enumerate(self.train_dataloader):
            self.optimizer.zero_grad()

            # TODO save input/output right before model(X)
            pred = self.model(X)
            loss = self.loss(pred, y)
            loss.backward()
            self.optimizer.step()

            if self.wandb:
                wandb.log({"Training Loss": loss.item()})

            if batch_idx % 100 == 0:
                print(f"Batch {batch_idx+1}/{len(self.train_dataloader)}: Loss: {loss.item()}")

    def test_loop(self):  # Top Level
        self.model.eval()
        test_loss = 0
        correct = 0

        with torch.no_grad():
            for X, y in self.test_dataloader:
                output = self.model(X)
                test_loss += self.loss(output, y, reduction='sum').item()
                pred = output.argmax(dim=1, keepdim=True)
                correct += pred.eq(y.view_as(pred)).sum().item()

        test_loss /= len(self.test_dataloader.dataset)

        print(f"\nTest set: Average loss: {test_loss:.4f}, Accuracy: {correct / len(self.test_dataloader.dataset):.4f}%")
        if self.wandb:
            wandb.log({"Test Loss": test_loss, "Test Accuracy": correct / len(self.test_dataloader.dataset)})

    def run(self):  # Run
        # TODO optional: clear temp folder
        self.clear_temp()

        for i in range(self.epochs):
            print(f"Epoch {i+1}")
            print("-" * 50)
            self.train_loop()
            self.test_loop()

            # TODO optionally save model


def train_wandb(config=None):
    with wandb.init(config=config):
        config = wandb.config
        epochs = 10
        trainer = TrainNetwork(config.batch_size, epochs, config.learning_rate, config.momentum, config.layers, config.optimizer, wandb_sweep=True)
        trainer.run()


if __name__ == "__main__":
    run_wandb = True
    if run_wandb:
        sweep_id = ""
        wandb.agent(sweep_id, train_wandb, count=50)
    else:
        wandb_single = True
        batch_size = 32
        epochs = 100
        learning_rate = 0.001
        momentum = 0
        network_idx = 0
        optimizer = 'adam'
        trainer = TrainNetwork(batch_size, epochs, learning_rate, momentum, network_idx, optimizer, wandb_single=wandb_single)
        trainer.run()
