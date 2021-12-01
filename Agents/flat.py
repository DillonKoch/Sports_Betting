# ==============================================================================
# File: flat.py
# Project: allison
# File Created: Sunday, 28th November 2021 10:18:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 28th November 2021 10:18:48 pm
# Modified By: Dillon Koch
# -----
#
# -----
# agent that makes simple flat bets using model predictions
# ==============================================================================


import copy
import datetime
import os
import sys
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Agents.agent_parent import Agent_Parent


class Flat(Agent_Parent):
    def __init__(self, league):
        super().__init__()
        self.league = league
        self.agent_name = "flat"

    def load_make_agent_bet_df(self):  # Top Level
        """
        loading the df of all the bets made by the agent, or making it if necessary
        """
        path = ROOT_PATH + f"/Data/Agent_Bets/{self.agent_name}.csv"
        if os.path.exists(path):
            agent_bet_df = pd.read_csv(path)
        else:
            cols = ['Date', 'Home', 'Away', 'Bet_Type', 'Models_Acc', 'Models_EV', 'Models_Pred',
                    'Bet', 'Bet_Val', 'Bet_ML', 'Wager', 'To_Win',
                    'Outcome', 'Profit', 'Running_Profit', 'Bet_ts']
            agent_bet_df = pd.DataFrame(columns=cols)
        return agent_bet_df

    def load_pred_df(self):  # Top Level
        """
        loading the df of all the predictions made by the models
        """
        path = ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv"
        pred_df = pd.read_csv(path)
        return pred_df

    def load_model_eval_df(self):  # Top Level
        """
        loading the df evaluating each model's performance in making bets at different thresholds
        """
        path = ROOT_PATH + f"/Data/Modeling_Eval/{self.league}/eval.csv"
        model_eval_df = pd.read_csv(path)
        return model_eval_df

    def find_games(self, bet_type, pred_df, upcoming_only):  # Top Level
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

    def top_models(self, pred_df, model_eval_df, bet_type, game, num=10):  # Top Level
        """
        finding the top applicable models (with thresholds) for a game/bet type
        """
        # we have a game -> find each model's prediction
        # find the top models with thresholds based on EV, loop through until 10 applicable ones are found
        # return those models
        model_eval_df_bet_type = model_eval_df.loc[model_eval_df['Bet_Type'] == bet_type]
        top_models = []
        for i, row in model_eval_df_bet_type.iterrows():
            pass
        return None

    def find_predictions(self, pred_df, bet_type, top_models, game):  # Top Level
        """
        finding the predictions for the top models for a game/bet type
        """
        pass

    def make_bets(self, top_models_predictions):  # Top Level
        pass

    def save_agent_bet_df(self, agent_bet_df):  # Top Level
        pass

    def run(self, upcoming_only=True):  # Run
        """
        making $5 bets when the top 10 models for a bet have positive EV
        """
        agent_bet_df = self.load_make_agent_bet_df()
        pred_df = self.load_pred_df()
        model_eval_df = self.load_model_eval_df()
        for bet_type in ['Spread', 'Total', 'Moneyline']:
            games = self.find_games(bet_type, pred_df, upcoming_only=upcoming_only)
            for game in games:
                top_models = self.top_models(pred_df, model_eval_df, bet_type, game, num=10)
                top_models_predictions = self.find_predictions(pred_df, bet_type, top_models, game)
                agent_bet_df = self.make_bets(top_models_predictions)
        self.save_agent_bet_df(agent_bet_df)
        print("DONE")


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        x = Flat(league)
        x.run()
