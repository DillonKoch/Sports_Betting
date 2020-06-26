# ==============================================================================
# File: prep_prod.py
# Project: Modeling
# File Created: Thursday, 25th June 2020 4:36:47 pm
# Author: Dillon Koch
# -----
# Last Modified: Friday, 26th June 2020 10:27:31 am
# Modified By: Dillon Koch
# -----
#
# -----
# This file prepares data from the PROD table for ML
# ==============================================================================


import sys
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

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
        self.all_teams = set(list(df.Home) + list(df.Away))
        if self.league == "NFL":
            self.all_teams = list(self.all_teams) + ["Las Vegas Raiders"]
            self.all_teams = list(set(self.all_teams))
        return df

    def remove_unplayed(self, prod_df):  # Top Level
        prod_df = prod_df.loc[["Final" in str(item) for item in list(prod_df.Final_Status)], :]
        return prod_df

    # @staticmethod
    # def win_pct(wins, losses):
    #     if ((wins > 0) and (losses == 0)):
    #         return 1
    #     elif sum([wins, losses]) == 0:
    #         return None
    #     else:
    #         return wins / losses

    # def clean_prod_records(self, prod_df):  # Top Level
    #     # add conf win % if ncaa
    #     def home_ovr_wl(row):
    #         home_rec = row['Home_Record'].split(',')[0]
    #         home_wins, home_losses = [int(item) for item in home_rec.split('-')][:2]
    #         home_won = True if int(row['Home_Score_x_x']) > int(row['Away_Score_x_x']) else False
    #         home_wins = home_wins - 1 if home_won else home_wins
    #         home_losses = home_losses - 1 if not home_won else home_losses
    #         return home_wins, home_losses

    #     def away_ovr_wl(row):
    #         away_rec = row['Away_Record'].split(',')[0]
    #         away_wins, away_losses = [int(item) for item in away_rec.split('-')][:2]
    #         home_won = True if int(row['Home_Score_x_x']) > int(row['Away_Score_x_x']) else False
    #         away_wins = away_wins - 1 if not home_won else away_wins
    #         away_losses = away_losses - 1 if home_won else away_losses
    #         return away_wins, away_losses

    #     def home_spec_wl(row):
    #         if ", Home" not in row["Home_Record"]:
    #             return 0, 0
    #         home_rec = row['Home_Record'].split(',')[1].strip()
    #         home_wins, home_losses = [int(item.replace(" Home", "")) for item in home_rec.split('-')][:2]
    #         home_won = True if int(row['Home_Score_x_x']) > int(row['Away_Score_x_x']) else False
    #         home_wins = home_wins - 1 if home_won else home_wins
    #         home_losses = home_losses - 1 if not home_won else home_losses
    #         return home_wins, home_losses

    #     def away_spec_wl(row):
    #         if ", Away" not in row["Away_Record"]:
    #             return 0, 0
    #         away_rec = row['Away_Record'].split(',')[1]
    #         away_wins, away_losses = [int(item.replace(" Away", "")) for item in away_rec.split('-')][:2]
    #         home_won = True if int(row['Home_Score_x_x']) > int(row['Away_Score_x_x']) else False
    #         away_wins = away_wins - 1 if not home_won else away_wins
    #         away_losses = away_losses - 1 if home_won else away_losses
    #         return away_wins, away_losses

    #     def home_conf_wl(row):
    #         pass

    #     def away_conf_wl(row):
    #         pass

    #     prod_df['Home_ovr_wins'] = prod_df.apply(lambda row: home_ovr_wl(row)[0], axis=1)
    #     prod_df['Home_ovr_losses'] = prod_df.apply(lambda row: home_ovr_wl(row)[1], axis=1)
    #     prod_df['Away_ovr_wins'] = prod_df.apply(lambda row: away_ovr_wl(row)[0], axis=1)
    #     prod_df['Away_ovr_losses'] = prod_df.apply(lambda row: away_ovr_wl(row)[1], axis=1)
    #     prod_df['Home_spec_wins'] = prod_df.apply(lambda row: home_spec_wl(row)[0], axis=1)
    #     prod_df['Home_spec_losses'] = prod_df.apply(lambda row: home_spec_wl(row)[1], axis=1)
    #     prod_df['Away_spec_wins'] = prod_df.apply(lambda row: away_spec_wl(row)[0], axis=1)
    #     prod_df['Away_spec_losses'] = prod_df.apply(lambda row: away_spec_wl(row)[1], axis=1)
    #     if self.league in ["NCAAF", "NCAAB"]:
    #         pass  # df apply here too
    #     return prod_df

    def _add_null_rec_cols(self, prod_df):  # Specific Helper clean_prod_records
        cols = ["Home_ovr_wins", "Home_ovr_losses", "Home_ovr_ties",
                "Away_ovr_wins", "Away_ovr_losses", "Away_ovr_ties",
                "Home_spec_wins", "Home_spec_losses", "Home_spec_ties",
                "Away_spec_wins", "Away_spec_losses", "Away_spec_ties",
                "conf_game", "neutral_game"]
        for col in cols:
            prod_df[col] = None
        return prod_df

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

        row["conf_game"] = True if home_tag == "conf" else False
        row["neutral_game"] = True if home_tag == "neutral" else False
        return row

    def clean_prod_records(self, prod_df):  # Top Level
        wl_dict = self._reset_wl_dict()
        current_season = int(prod_df.iloc[0, :]['Season_x'])
        prod_df = self._add_null_rec_cols(prod_df)

        for i, row in tqdm(prod_df.iterrows()):
            wl_dict, current_season = self._new_season_check(row, current_season, wl_dict)

            prod_df.iloc[i, :] = self._update_row(row, wl_dict)

            wl_dict = self._update_wl_dict(wl_dict, row)
        return prod_df

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
    self = x
    prod_df = x.load_prod_df()
    prod_df = x.remove_unplayed(prod_df)
    prod_df = x.clean_prod_records(prod_df)
    # prod_df = x.clean_prod_records(prod_df)
    df = x.run()
