# ==============================================================================
# File: agent_parent.py
# Project: allison
# File Created: Sunday, 28th November 2021 10:15:32 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 28th November 2021 10:15:33 pm
# Modified By: Dillon Koch
# -----
#
# -----
# parent class for betting agents
# ==============================================================================


import abc
import copy
import datetime
import os
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Agent_Parent(abc.ABC):
    def __init__(self):
        self.thresh_desc = ""

    @property
    def prediction_df_path(self):  # Property
        return ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv"

    @property
    def bet_df_path(self):  # Property
        return ROOT_PATH + f"/Data/Agent_Bets/{self.league}/{self.agent_name}{self.thresh_desc}.csv"

    def _current_ts(self):  # Global Helper
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def load_prediction_df(self):  # Top Level
        """
        loads the df with all the models' predictions
        """
        return pd.read_csv(self.prediction_df_path)

    def load_make_agent_bet_df(self):  # Top Level
        """
        loading the df of all the bets made by the agent, or making it if necessary
        """
        path = ROOT_PATH + f"/Data/Agent_Bets/{self.agent_name}.csv"
        if os.path.exists(path):
            agent_bet_df = pd.read_csv(path)
        else:
            cols = ['Date', 'Home', 'Away', 'Bet_Type', 'Models_Acc', 'Models_EV', 'Models_Pred',
                    'Bet_Val', 'Bet_ML', 'Wager', 'To_Win',
                    'Outcome', 'Profit', 'Running_Profit', 'Bet_ts']
            agent_bet_df = pd.DataFrame(columns=cols)
        return agent_bet_df

    def load_pred_df(self, prod):  # Top Level
        """
        loading the df of all the predictions made by the models
        """
        prod_test_str = "Prod" if prod else "Test"
        path = ROOT_PATH + f"/Data/Predictions/{self.league}/{prod_test_str}_Predictions.csv"
        pred_df = pd.read_csv(path)
        return pred_df

    def load_model_eval_df(self):  # Top Level
        """
        loading the df evaluating each model's performance in making bets at different thresholds
        """
        path = ROOT_PATH + f"/Data/Modeling_Eval/{self.league}/Test_models.csv"
        model_eval_df = pd.read_csv(path)
        return model_eval_df

    def find_games(self, pred_df, upcoming_only):  # Top Level
        """
        finding games to bet on in pred_df
        - can focus on upcoming games only, or all past games
        """
        if upcoming_only:
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            games_df = pred_df.loc[pred_df['Game_Date'] >= today]
        else:
            games_df = copy.deepcopy(pred_df)

        games_hads = [(home, away, date) for home, away, date in
                      zip(games_df['Home'], games_df['Away'], games_df['Game_Date'])]
        return list(set(games_hads))

    def top_models(self, model_eval_df, bet_type):  # Top Level
        bet_eval_df = model_eval_df.loc[model_eval_df['Bet_Type'] == bet_type]
        top_models = bet_eval_df.to_dict('records')
        return top_models

    def _model_pred(self, model, bet_type, game, pred_df):  # Specific Helper top_model_predictions
        bet_df = pred_df.loc[pred_df['Bet_Type'] == bet_type]
        game_df = bet_df.loc[(bet_df['Home'] == game[0]) & (bet_df['Away'] == game[1]) & (bet_df['Game_Date'] == game[2])]
        game_df.reset_index(inplace=True, drop=True)
        for key in ['Algorithm', 'Player_Stats', 'Avg_Past_Games', 'Dataset']:
            game_df = game_df.loc[game_df[key] == model[key]]
            game_df.reset_index(inplace=True, drop=True)

        return game_df if len(game_df) > 0 else None

    def top_model_predictions(self, bet_type, game, top_models, pred_df):  # Top Level
        top_model_pred_dfs = []
        top_applicable_models = []
        for top_model in top_models:
            game_df = self._model_pred(top_model, bet_type, game, pred_df)
            if game_df is None:
                continue

            if abs(game_df['Prediction'].values[0] - 0.5) > (top_model['Threshold'] - 0.5):
                top_model_pred_dfs.append(game_df)
                top_applicable_models.append(top_model)
        return top_model_pred_dfs, top_applicable_models

    def _to_win(self, wager, bet_ml):  # Specific Helper make_bets
        """
        computing the amount a wager would win if it hits based on the moneyline
        """
        if bet_ml < 0:
            to_win = wager * (100 / abs(bet_ml))
        else:
            to_win = wager * (bet_ml / 100)
        return round(to_win, 2)

    def _model_acc_ev_pred(self, top_applicable_models, top_model_pred_dfs):  # Specific Helper make_bets
        models_acc = round(np.mean([tam['Accuracy'] for tam in top_applicable_models]), 2)
        models_ev = round(np.mean([tam['Expected_Value'] for tam in top_applicable_models]), 2)
        models_pred = round(np.mean([tmpdf['Prediction'].values[0] for tmpdf in top_model_pred_dfs]), 2)
        return models_acc, models_ev, models_pred

    def _bet_val_ml(self, top_model_pred_dfs):  # Specific Helper make_bets
        bet_val = top_model_pred_dfs[0]['Bet_Value'].values[0]
        bet_ml = top_model_pred_dfs[0]['Bet_ML'].values[0]  # TODO needs work - make sure we have the other side of ML bets!
        return bet_val, bet_ml

    @abc.abstractmethod
    def make_bets(self):  # Top Level  Done
        """
        each agent will have its own way of making bets
        """
        pass

    def save_agent_bet_df(self, agent_bet_df):  # Top Level
        path = ROOT_PATH + f"/Data/Agent_Bets/{self.league}/{self.agent_name}.csv"
        agent_bet_df.to_csv(path, index=False)

    def run(self, prod=True):
        """
        making $5 bets on prod/test games when the top 10 models for a bet have positive EV
        """
        agent_bet_df = self.load_make_agent_bet_df()
        pred_df = self.load_pred_df(prod)
        model_eval_df = self.load_model_eval_df()
        games = self.find_games(pred_df, True)
        for bet_type in ['Spread', 'Total', 'Moneyline']:
            print(bet_type)
            top_models = self.top_models(model_eval_df, bet_type)
            for game in tqdm(games):
                top_model_pred_dfs, top_applicable_models = self.top_model_predictions(bet_type, game, top_models, pred_df)
                agent_bet_df = self.make_bets(agent_bet_df, bet_type, game, top_model_pred_dfs, top_applicable_models)
        self.save_agent_bet_df(agent_bet_df)
        print("DONE")


if __name__ == '__main__':
    x = Agent_Parent()
    self = x
    x.run()
