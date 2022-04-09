# ==============================================================================
# File: frontend.py
# Project: allison
# File Created: Thursday, 7th April 2022 5:28:05 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 7th April 2022 5:28:06 pm
# Modified By: Dillon Koch
# -----
#
# -----
# uploading predictions, labels, game info to MongoDB for the frontend
# ==============================================================================


import datetime
import sys
from os.path import abspath, dirname

import pandas as pd
from pymongo import MongoClient
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Frontend:
    def __init__(self, league):
        self.league = league

    def load_pred_df(self):  # Top Level
        """
        loading predictions df
        """
        path = ROOT_PATH + f"/Data/Predictions/{self.league}/Predictions.csv"
        df = pd.read_csv(path)
        return df

    def filter_recent_preds(self, df):  # Top Level
        """
        filtering the df down to just the most recent predictions (last 7 days)
        """
        df['Date'] = pd.to_datetime(df['Date'])
        last_week = datetime.datetime.today() - datetime.timedelta(days=7)
        df = df.loc[df['Date'] > last_week]
        return df

    def _load_collection(self):  # Specific Helper  upload_preds
        """
        loading the collection from mongodb
        """
        cluster = MongoClient("mongodb+srv://DillonKoch:QBface14$@personal-website-cluste.zuunk.mongodb.net/myFirstDatabase?retryWrites=true&w=majority")
        db = cluster["SportsBetting"]
        collection = db["Predictions"]
        return collection

    def _clean_row_dict(self, row_dict):  # Specific Helper upload_preds
        row_dict['_id'] = f"{self.league} {row_dict['Date']} {row_dict['Home']} {row_dict['Away']} {row_dict['Bet_Type']}"
        row_dict['Date'] = row_dict['Date'].strftime('%Y-%m-%d')

        row_dict['Odds'] = row_dict['Bet_Value']
        row_dict['ML'] = row_dict['Bet_ML']
        if row_dict['Prediction'] > 0.5:
            row_dict['Bet'] = row_dict['Home'] if row_dict['Bet_Type'] == "Spread" else "Over"
        else:
            row_dict['Bet'] = row_dict['Away'] if row_dict['Bet_Type'] == "Spread" else "Under"

        row_dict['Confidence'] = row_dict['Prediction'] if row_dict['Prediction'] > 0.5 else (1 - row_dict['Prediction'])
        row_dict['Confidence'] *= 100
        row_dict['League'] = self.league
        return row_dict

    def upload_preds(self, df):  # Top Level
        """
        uploading all the rows/predictions from the df to mongodb
        """
        row_dicts = df.to_dict('records')
        collection = self._load_collection()
        for row_dict in tqdm(row_dicts):
            row_dict = self._clean_row_dict(row_dict)
            try:
                collection.insert_one(row_dict)
                print('insert')
            except BaseException as e:
                print(e)
                collection.replace_one({"_id": row_dict['_id']}, row_dict)
                print('replace')
        print("DONE")

    def run(self):  # Run
        pred_df = self.load_pred_df()
        recent_preds = self.filter_recent_preds(pred_df)
        self.upload_preds(recent_preds)


if __name__ == '__main__':
    league = "NBA"
    x = Frontend(league)
    self = x
    x.run()
