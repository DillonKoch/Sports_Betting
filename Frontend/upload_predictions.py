# ==============================================================================
# File: upload_predictions.py
# Project: allison
# File Created: Wednesday, 8th December 2021 9:15:51 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 8th December 2021 9:15:52 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Uploading prediction data to MongoDB
# ==============================================================================


import os
import sys
from os.path import abspath, dirname

import pandas as pd
import pymongo
from pymongo import MongoClient
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Upload_Predictions:
    def __init__(self):
        self.mdb_pred_cols = ['League', 'Date', 'Home', 'Away', 'Bet_Type', 'Odds', 'ML', 'Bet', 'Confidence', 'Outcome', 'Uploaded']
        self.mdb_pred_df_path = ROOT_PATH + f'/Data/Predictions/MongoDB_Predictions.csv'
        self.collection = self.load_collection()

    def load_collection(self):
        cluster = MongoClient("mongodb+srv://DillonKoch:QBface14$@personal-website-cluste.zuunk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = cluster["SportsBetting"]
        collection = db["Predictions"]
        return collection

    def load_mdb_pred_df(self):  # Top Level
        """
        loading/creating the dataframe of predictions cleaned for MongoDB
        """
        if os.path.exists(self.mdb_pred_df_path):
            df = pd.read_csv(self.mdb_pred_df_path)
        else:
            df = pd.DataFrame(columns=self.mdb_pred_cols)
        return df

    def load_league_pred_df(self, league):  # Top Level
        """
        loading the Prod_Predictions.csv for a league
        """
        path = ROOT_PATH + f'/Data/Predictions/{league}/Prod_Predictions.csv'
        return pd.read_csv(path)

    def get_games(self, league_pred_df):  # Top Level
        """
        grabbing tuples of (Home, Away, Date) from the Prod_Predictions.csv for each game
        - making sure they're not already in the MongoDB_Predictions.csv
        """
        homes = list(league_pred_df['Home'])
        aways = list(league_pred_df['Away'])
        dates = list(league_pred_df['Game_Date'])
        all_games = [(home, away, date) for home, away, date in zip(homes, aways, dates)]
        return list(set(all_games))

    def game_pred_odds_ml(self, league_pred_df, game, bet_type):  # Top Level
        game_df = league_pred_df.loc[(league_pred_df['Home'] == game[0]) & (league_pred_df['Away'] == game[1]) & (league_pred_df['Game_Date'] == game[2])]
        bet_df = game_df.loc[game_df['Bet_Type'] == bet_type]
        bet_df = bet_df.loc[bet_df['Player_Stats'] == True]
        preds = list(bet_df['Prediction'])
        pred = sum(preds) / len(preds)
        bet_value = bet_df['Bet_Value'].values[0]
        ml = bet_df['Bet_ML'].values[0]
        return pred, bet_value, ml

    def _bet_from_pred(self, bet_type, pred):  # Specific Helper
        negative_dict = {"Spread": "Away", "Total": "Under", "Moneyline": "Away"}
        positive_dict = {"Spread": "Home", "Total": "Over", "Moneyline": "Home"}
        bet = negative_dict[bet_type] if pred < 0.5 else positive_dict[bet_type]
        return bet

    def update_mdb_pred_df(self, mdb_pred_df, games, pred_odds_mls, league, bet_type):  # Top Level
        """
        looping through the data to update the MongoDB dataframe
        """
        for game, pred_odds_ml in zip(games, pred_odds_mls):
            home, away, date = game
            pred, odds, ml = pred_odds_ml
            bet = self._bet_from_pred(bet_type, pred)
            confidence = round((abs(pred - 0.5) + 0.5) * 100, 2)
            new_row = [league, date, home, away, bet_type, odds, ml, bet, confidence, None, False]
            mdb_pred_df.loc[len(mdb_pred_df)] = new_row
        return mdb_pred_df

    def upload_mdb_pred_df(self, mdb_pred_df):  # Top Level
        print("uploading to mongodb...")
        row_dicts = mdb_pred_df.to_dict('records')
        for row_dict in tqdm(row_dicts):
            row_dict['_id'] = f"{row_dict['League']} {row_dict['Date']} {row_dict['Home']} {row_dict['Away']} {row_dict['Bet_Type']}"
            try:
                self.collection.insert_one(row_dict)
                print('insert')
            except Exception as e:
                print(e)
                self.collection.replace_one({"_id": row_dict['_id']}, row_dict)
                print('replace')
            print('here')

    def save_mdb_pred_df(self, mdb_pred_df):  # Top Level
        """
        saving the dataframe of predictions cleaned for MongoDB
        """
        mdb_pred_df.drop_duplicates(subset=['League', 'Date', 'Home', 'Away', 'Bet_Type'], keep="last", inplace=True)
        mdb_pred_df.sort_values(by=['Date', 'League', 'Home', 'Away', 'Bet_Type'], inplace=True)
        mdb_pred_df.to_csv(self.mdb_pred_df_path, index=False)
        return mdb_pred_df

    def run(self):  # Run
        mdb_pred_df = self.load_mdb_pred_df()
        # for league in ['NFL', 'NBA', 'NCAAF', 'NCAAB']:
        for league in ['NFL']:
            league_pred_df = self.load_league_pred_df(league)
            games = self.get_games(league_pred_df)
            for bet_type in ['Spread', 'Total', 'Moneyline']:
                pred_odds_mls = [self.game_pred_odds_ml(league_pred_df, game, bet_type) for game in games]
                mdb_pred_df = self.update_mdb_pred_df(mdb_pred_df, games, pred_odds_mls, league, bet_type)
        self.save_mdb_pred_df(mdb_pred_df)
        self.upload_mdb_pred_df(mdb_pred_df)
        print("DONE")


if __name__ == '__main__':
    x = Upload_Predictions()
    self = x
    x.run()
