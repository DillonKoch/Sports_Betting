# ==============================================================================
# File: alignment.py
# Project: Sports_Betting
# File Created: Wednesday, 3rd June 2020 3:50:36 pm
# Author: Dillon Koch
# -----
# Last Modified: Wednesday, 3rd June 2020 8:10:16 pm
# Modified By: Dillon Koch
# -----
# Collins Aerospace
#
# -----
# Aligning ESPN-scraped data with Odds data from the "Odds" folder
# ==============================================================================


import datetime
import os
import sys
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Alignment:
    def __init__(self, league):
        self.league = league
        self.teams = os.listdir("./Data/{}/".format(self.league))

    def _remove_preseason(self, df):  # Specific Helper load_espn_data
        df = df[df.Week != "HOF"]

        def add_dt(row):
            return datetime.datetime.strptime(row['Date'], "%B %d, %Y")

        df['datetime'] = df.apply(lambda row: add_dt(row), axis=1)
        df.sort_values(by='datetime')
        df.drop_duplicates(subset="datetime", keep="last")

        return df

    def load_espn_data(self):  # Top Level
        all_dfs = []
        for team in tqdm(self.teams):
            df_names = [item for item in os.listdir("./Data/{}/{}/".format(self.league, team))
                        if (('.csv' in item) and (int(item[-8:-4]) > 2006))]
            for df_name in df_names:
                full_path = "./Data/{}/{}/{}".format(self.league, team, df_name)
                df = pd.read_csv(full_path)
                df = self._remove_preseason(df)
                all_dfs.append(df)

        full_df = pd.concat(all_dfs)
        full_df.drop_duplicates(subset="ESPN_ID", inplace=True)
        full_df.sort_values(by="ESPN_ID", inplace=True)
        return full_df

    def load_odds_data(self):  # Top Level
        all_dfs = []
        csv_names = [item for item in os.listdir("./Odds/{}".format(self.league)) if '.csv' in item]
        for csv_name in csv_names:
            full_path = "./Odds/{}/{}".format(self.league, csv_name)
            df = pd.read_csv(full_path)
            all_dfs.append(df)

        full_df = pd.concat(all_dfs)
        return full_df

    def games_from_odds(self, odds_df):  # Top Level
        pass

    def run(self):  # Run
        espn_df = self.load_espn_data()
        odds_df = self.load_odds_data()


if __name__ == "__main__":
    x = Alignment("NFL")
    self = x

    espn_df = x.load_espn_data()
    odds_df = x.load_odds_data()
