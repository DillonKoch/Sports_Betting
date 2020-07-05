# ==============================================================================
# File: prep_prod.py
# Project: Modeling
# File Created: Thursday, 25th June 2020 4:36:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 5th July 2020 3:27:51 pm
# Modified By: Dillon Koch
# -----
#
# -----
# This file prepares data from the PROD table for ML
# This is done for both finished games and games not yet played (for prediction)
# ==============================================================================


import json
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Prep_Prod:
    def __init__(self, league: str):
        self.league = league

    @property
    def config(self):
        with open(ROOT_PATH + "/Modeling/{}_model.json".format(self.league.lower())) as f:
            config = json.load(f)
        return config

    def load_prod_df(self):  # Top Level
        df = pd.read_csv(ROOT_PATH + "/PROD/{}_PROD.csv".format(self.league))
        df = df.replace("San Diego Chargers", "Los Angeles Chargers")
        df = df.replace("Oakland Raiders", "Las Vegas Raiders")
        df = df.replace("St. Louis Rams", "Los Angeles Rams")
        self.all_teams = set(list(df.Home) + list(df.Away))
        return df

    def _clean_unplayed_records(self, prod_df: pd.DataFrame) -> pd.DataFrame:  # Specific Helper clean_prod_records
        prod_df.Home_Record.fillna("0-0, 0-0 Home", inplace=True)
        prod_df.Away_Record.fillna("0-0, 0-0 Away", inplace=True)
        return prod_df

    def _add_null_rec_cols(self, df: pd.DataFrame) -> pd.DataFrame:  # Specific Helper clean_prod_records
        record_cols = ["Home_ovr_wins", "Home_ovr_losses", "Home_ovr_ties",
                       "Away_ovr_wins", "Away_ovr_losses", "Away_ovr_ties",
                       "Home_spec_wins", "Home_spec_losses", "Home_spec_ties",
                       "Away_spec_wins", "Away_spec_losses", "Away_spec_ties",
                       "conf_game", "neutral_game"]
        for col in record_cols:
            df[col] = None
        return df

    def _new_season_check(self, row, current_season, wl_dict):  # Specific Helper clean_prod_records
        is_new_season = True if int(row['Season_x']) > current_season else False
        if is_new_season:
            wl_dict = self._reset_wl_dict()
            current_season += 1
        return wl_dict, current_season

    def _reset_wl_dict(self):  # Specific Helper clean_prod_records
        return {team: {"ovr_wins": 0, "ovr_losses": 0, "ovr_ties": 0,
                       "home_wins": 0, "home_losses": 0, "home_ties": 0,
                       "away_wins": 0, "away_losses": 0, "away_ties": 0,
                       "conf_wins": 0, "conf_losses": 0, "conf_ties": 0,
                       "neutral_wins": 0, "neutral_losses": 0, "neutral_ties": 0} for team in self.all_teams}

    def _update_wl_dict(self, wl_dict, row):  # Specific Helper clean_prod_records
        if "Final" not in str(row["Final_Status"]):
            return wl_dict

        home, away = row["Home"], row["Away"]
        home_tag = "home" if "Home" in row["Home_Record"] else "conf" if "Conf" in row['Home_Record'] else "neutral"
        away_tag = "away" if "Away" in row["Away_Record"] else "conf" if "Conf" in row['Away_Record'] else "neutral"

        tie = True if int(row['Home_Score_x']) == int(row['Away_Score_x']) else False
        if tie:
            wl_dict[home]["ovr_ties"] += 1
            wl_dict[away]["ovr_ties"] += 1
            wl_dict[home]["{}_ties".format(home_tag)] += 1
            wl_dict[away]["{}_ties".format(away_tag)] += 1
            return wl_dict

        home_won = True if int(row['Home_Score_x']) > int(row['Away_Score_x']) else False
        if home_won:
            wl_dict[home]["ovr_wins"] += 1
            wl_dict[away]["ovr_losses"] += 1
            wl_dict[home]["{}_wins".format(home_tag)] += 1
            wl_dict[away]["{}_losses".format(away_tag)] += 1
        else:
            wl_dict[home]["ovr_losses"] += 1
            wl_dict[away]["ovr_wins"] += 1
            wl_dict[home]["{}_losses".format(home_tag)] += 1
            wl_dict[away]["{}_wins".format(away_tag)] += 1
        return wl_dict

    def _update_row(self, row, wl_dict):  # Specific Helper clean_prod_records
        home, away = row["Home"], row["Away"]
        home_tag = "home" if "Home" in row["Home_Record"] else "conf" if "Conf" in row['Home_Record'] else "neutral"
        away_tag = "away" if "Away" in row["Away_Record"] else "conf" if "Conf" in row['Away_Record'] else "neutral"

        row["Home_ovr_wins"] = wl_dict[home]["ovr_wins"]
        row["Home_ovr_losses"] = wl_dict[home]["ovr_losses"]
        row["Home_ovr_ties"] = wl_dict[home]["ovr_ties"]
        row["Away_ovr_wins"] = wl_dict[away]["ovr_wins"]
        row["Away_ovr_losses"] = wl_dict[away]["ovr_losses"]
        row["Away_ovr_ties"] = wl_dict[away]["ovr_ties"]

        row["Home_spec_wins"] = wl_dict[home]["{}_wins".format(home_tag)]
        row["Home_spec_losses"] = wl_dict[home]["{}_losses".format(home_tag)]
        row["Home_spec_ties"] = wl_dict[home]["{}_ties".format(home_tag)]
        row["Away_spec_wins"] = wl_dict[away]["{}_wins".format(away_tag)]
        row["Away_spec_losses"] = wl_dict[away]["{}_losses".format(away_tag)]
        row["Away_spec_ties"] = wl_dict[away]["{}_ties".format(away_tag)]

        row["conf_game"] = 1 if home_tag == "conf" else 0
        row["neutral_game"] = 1 if home_tag == "neutral" else 0
        return row

    def clean_prod_records(self, prod_df):  # Top Level
        prod_df = self._clean_unplayed_records(prod_df)
        wl_dict = self._reset_wl_dict()
        current_season = int(prod_df.iloc[0, :]['Season_x'])
        prod_df = self._add_null_rec_cols(prod_df)

        for i, row in tqdm(prod_df.iterrows()):
            wl_dict, current_season = self._new_season_check(row, current_season, wl_dict)
            prod_df.iloc[i, :] = self._update_row(row, wl_dict)
            wl_dict = self._update_wl_dict(wl_dict, row)

        ml_cols = ["Home_ovr_wins", "Home_ovr_losses", "Home_ovr_ties",
                   "Away_ovr_wins", "Away_ovr_losses", "Away_ovr_ties",
                   "Home_spec_wins", "Home_spec_losses", "Home_spec_ties",
                   "Away_spec_wins", "Away_spec_losses", "Away_spec_ties",
                   "conf_game", "neutral_game"]
        return prod_df, ml_cols

    @staticmethod
    def normalize(nums):  # Global Helper
        nums = [float(item) for item in nums]
        min_num = np.min(nums)
        max_num = np.max(nums)
        return [((item - min_num) / (max_num - min_num)) for item in nums]

    def clean_week(self, prod_df):  # Top Level
        if self.league != "NFL":
            return prod_df
        prod_week_vals = list(prod_df.Week)
        prod_week_vals = [
            item.replace("WC", '18').replace("DIV", '19').replace("CONF", '20').replace("SB", '21') for item in prod_week_vals]
        prod_df.Week = pd.Series(self.normalize(prod_week_vals))
        return prod_df, ["Week"]

    def clean_season(self, prod_df):  # Top Level
        season_vals = list(prod_df.Season_x)
        prod_df.Season_x = pd.Series(self.normalize(season_vals))
        return prod_df, ["Season_x"]

    def clean_stats(self, prod_df):  # Top Level
        # goal is to get all info represented in cols that can be scaled 0-1
        pass

    def add_dummies(self, df, prod_df):  # Top Level
        dummy_cols = ["Home", "Away", "Network"]
        for col in dummy_cols:
            new_dummy_df = pd.get_dummies(prod_df[col], prefix=col)
            df = pd.concat([df, new_dummy_df], axis=1)
        return df

    # def add_dash_cols(self, df):
    #     df['num_penalties'] = df.apply(lambda row: row['home_penalties'].split('-')[0], axis=1)
    #     df['penalty_yards'] = df.apply(lambda row: row['home_penalties'].split('-')[1], axis=1)
    #     return df

    def run(self):  # Run
        """
        starting with a blank df and prod df, then as I clean and modify each section of PROD for ML,
        I'll also update my ML dataset at that time
        """
        prod_df = self.load_prod_df()
        prod_df, record_ml_cols = self.clean_prod_records(prod_df)
        prod_df, week_ml_cols = self.clean_week(prod_df)
        prod_df, season_ml_cols = self.clean_season(prod_df)
        # prod_df, stats_ml_cols = self.clean_stats(prod_df)

        df = pd.DataFrame()
        df = self.add_dummies(df, prod_df)
        ml_cols = record_ml_cols + week_ml_cols + season_ml_cols + stats_ml_cols
        prod_ml = prod_df.loc[:, ml_cols]
        df = pd.concat([df, prod_ml], axis=1)
        return df


# MAKE ONE LOOP THAT RUNS .ITERROWS() AND HAVE A BUNCH OF METHODS THAT ALL CHANGE THE CURRENT ROW AT ONCE


if __name__ == "__main__":
    nfl = Prep_Prod("NFL")
    nba = Prep_Prod("NBA")
    ncaaf = Prep_Prod("NCAAF")
    ncaab = Prep_Prod("NCAAB")
    self = nfl
    # df, prod_df = self.run()


# idea for showing average stats:
    # compute the running average for each week like with wins and losses
    # then for week 1 of the following year, use the average I have from the last year
    # just don't reset the dict until after using the values for week 1 of the new year
