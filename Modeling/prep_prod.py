# ==============================================================================
# File: prep_prod.py
# Project: Modeling
# File Created: Thursday, 25th June 2020 4:36:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Thursday, 25th June 2020 8:38:49 pm
# Modified By: Dillon Koch
# -----
#
# -----
# This file prepares data from the PROD table for ML
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Prep_Prod:
    def __init__(self, league):
        self.league = league

    @property
    def remove_cols(self):  # Property
        all_leagues = ["ESPN_ID", "Season_x", "Date", "League", "Title", "Game_Time", "scraped_ts"]
        nfl = ["Week"]
        return all_leagues + nfl if self.league == "NFL" else all_leagues

    @property
    def dummy_cols(self):  # Property
        all_leagues = ["Home", "Away"]
        return all_leagues

    def load_prod_df(self):  # Top Level
        df = pd.read_csv(ROOT_PATH + "/PROD/{}_PROD.csv".format(self.league))
        include_cols = [col for col in list(df.columns) if col not in self.remove_cols]
        df = df.loc[:, include_cols]
        return df

    def remove_unplayed(self, prod_df):  # Top Level
        prod_df = prod_df.loc[["Final" in str(item) for item in list(prod_df.Final_Status)], :]
        return prod_df

    @staticmethod
    def win_pct(wins, losses):
        if ((wins > 0) and (losses == 0)):
            return 1
        elif sum([wins, losses]) == 0:
            return None
        else:
            return wins / losses

    def clean_prod_records(self, prod_df):  # Top Level
        # add conf win % if ncaa
        def home_ovr_wl(row):
            home_rec = row['Home_Record'].split(',')[0]
            home_wins, home_losses = [int(item) for item in home_rec.split('-')][:2]
            home_won = True if int(row['Home_Score_x']) > int(row['Away_Score_x']) else False
            home_wins = home_wins - 1 if home_won else home_wins
            home_losses = home_losses - 1 if not home_won else home_losses
            return home_wins, home_losses

        def away_ovr_wl(row):
            away_rec = row['Away_Record'].split(',')[0]
            away_wins, away_losses = [int(item) for item in away_rec.split('-')][:2]
            home_won = True if int(row['Home_Score_x']) > int(row['Away_Score_x']) else False
            away_wins = away_wins - 1 if not home_won else away_wins
            away_losses = away_losses - 1 if home_won else away_losses
            return away_wins, away_losses

        def home_spec_wl(row):
            if ", Home" not in row["Home_Record"]:
                return 0, 0
            home_rec = row['Home_Record'].split(',')[1].strip()
            home_wins, home_losses = [int(item.replace(" Home", "")) for item in home_rec.split('-')][:2]
            home_won = True if int(row['Home_Score_x']) > int(row['Away_Score_x']) else False
            home_wins = home_wins - 1 if home_won else home_wins
            home_losses = home_losses - 1 if not home_won else home_losses
            return home_wins, home_losses

        def away_spec_wl(row):
            if ", Away" not in row["Away_Record"]:
                return 0, 0
            away_rec = row['Away_Record'].split(',')[1]
            away_wins, away_losses = [int(item.replace(" Away", "")) for item in away_rec.split('-')][:2]
            home_won = True if int(row['Home_Score_x']) > int(row['Away_Score_x']) else False
            away_wins = away_wins - 1 if not home_won else away_wins
            away_losses = away_losses - 1 if home_won else away_losses
            return away_wins, away_losses

        def home_conf_wl(row):
            pass

        def away_conf_wl(row):
            pass

        prod_df['Home_ovr_wins'] = prod_df.apply(lambda row: home_ovr_wl(row)[0], axis=1)
        prod_df['Home_ovr_losses'] = prod_df.apply(lambda row: home_ovr_wl(row)[1], axis=1)
        prod_df['Away_ovr_wins'] = prod_df.apply(lambda row: away_ovr_wl(row)[0], axis=1)
        prod_df['Away_ovr_losses'] = prod_df.apply(lambda row: away_ovr_wl(row)[1], axis=1)
        prod_df['Home_spec_wins'] = prod_df.apply(lambda row: home_spec_wl(row)[0], axis=1)
        prod_df['Home_spec_losses'] = prod_df.apply(lambda row: home_spec_wl(row)[1], axis=1)
        prod_df['Away_spec_wins'] = prod_df.apply(lambda row: away_spec_wl(row)[0], axis=1)
        prod_df['Away_spec_losses'] = prod_df.apply(lambda row: away_spec_wl(row)[1], axis=1)
        if self.league in ["NCAAF", "NCAAB"]:
            pass  # df apply here too
        return prod_df

    def add_records(self):
        # NEW WAY OF ADDING WINS AND LOSSES IN THE DATAFRAME:
        # CREATE A DEFAULTDICT OR SOME DICT THAT KEEPS TRACK OF EACH TEAM'S W/L RECORD
        # IN TERMS OF HOME/AWAY, OVERALL, AND CONFERENCE
        # THEN GO THROUGH ALL THE ROWS, UPDATING THE DICT AND INSERTING VALUES FOR EACH GAME
        # THAT WAY i CAN GET HOME/AWAY SPECIFICALLY FOR COLLEGE SPORTS
        # AND THIS WILL MAKE IT EASIER FOR NFL AND NBA PLAYOFFS WHEN ESPN DOESN'T UPDATE

    def add_dummies(self, df, prod_df):  # Top Level
        for col in self.dummy_cols:
            new_dummy_df = pd.get_dummies(prod_df[col], prefix=col)
            df = pd.concat([df, new_dummy_df], axis=1)
        return df

    def add_record_cols(self, df, prod_df):
        def add_home(row):
            if "Home" in row:
                pass

    def run(self):  # Run
        prod_df = self.load_prod_df()
        prod_df = self.remove_unplayed(prod_df)
        df = pd.DataFrame()
        df = self.add_dummies(df, prod_df)

        return df


if __name__ == "__main__":
    x = Prep_Prod("NFL")
    prod_df = x.load_prod_df()
    prod_df = x.remove_unplayed(prod_df)
    prod_df = x.clean_prod_records(prod_df)
    df = x.run()
