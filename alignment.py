# ==============================================================================
# File: alignment.py
# Project: Sports_Betting
# File Created: Wednesday, 3rd June 2020 3:50:36 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 6th June 2020 7:01:36 pm
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

import copy
import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Odds_Game:
    def __init__(self):
        self.Season = None


class Alignment:
    def __init__(self, league):
        self.league = league
        self.teams = os.listdir("./Data/{}/".format(self.league))

    @property
    def odds_conversion_dict(self):  # Property
        conversion_dict = {
            "NewEngland": "New England Patriots",
            "GreenBay": "Green Bay Packers",
            "Seattle": "Seattle Seahawks",
            "Baltimore": "Baltimore Ravens",
            "Pittsburgh": "Pittsburgh Steelers",
            "Indianapolis": "Indianapolis Colts",
            "NewOrleans": "New Orleans Saints",
            "Philadelphia": "Philadelphia Eagles",
            "KansasCity": "Kansas City Chiefs",
            "SanFrancisco": "San Francisco 49ers",
            "Atlanta": "Atlanta Falcons",
            "Denver": "Denver Broncos",
            "NYGiants": "New York Giants",
            "Minnesota": "Minnesota Vikings",
            "Arizona": "Arizona Cardinals",
            "Carolina": "Carolina Panthers",
            "Dallas": "Dallas Cowboys",
            "Tennessee": "Tennessee Titans",
            "NYJets": "New York Jets",
            "Cincinnati": "Cincinnati Bengals",
            "Jacksonville": "Jacksonville Jaguars",
            "Chicago": "Chicago Bears",
            "Washington": "Washington Redskins",
            "Detroit": "Detroit Lions",
            "Buffalo": "Buffalo Bills",
            "Miami": "Miami Dolphins",
            "Oakland": "Oakland Raiders",
            "TampaBay": "Tampa Bay Buccaneers",
            "Cleveland": "Cleveland Browns",
            "Houston": "Houston Texans",
            "SanDiego": "San Diego Chargers",
            "St.Louis": "St. Louis Rams",
            "LARams": "Los Angeles Rams",
            "LAChargers": "Los Angeles Chargers",
            "HoustonTexans": "Houston Texans",
            "LosAngeles": "Los Angeles Rams"
        }
        return conversion_dict

    @property
    def season_start_dict(self):  # Property
        start_dict = {
            "2007": datetime.date(2007, 9, 6),
            "2008": datetime.date(2008, 9, 4),
            "2009": datetime.date(2009, 9, 10),
            "2010": datetime.date(2010, 9, 9),
            "2011": datetime.date(2011, 9, 8),
            "2012": datetime.date(2012, 9, 5),
            "2013": datetime.date(2013, 9, 5),
            "2014": datetime.date(2014, 9, 4),
            "2015": datetime.date(2015, 9, 10),
            "2016": datetime.date(2016, 9, 8),
            "2017": datetime.date(2017, 9, 7),
            "2018": datetime.date(2018, 9, 6),
            "2019": datetime.date(2019, 9, 5),
        }
        return start_dict

    def _get_df_paths(self):  # Specific Helper load_espn_data
        df_paths = []
        for team in self.teams:
            team_paths = [item for item in os.listdir("./Data/{}/{}/".format(self.league, team))]
            team_paths = [item for item in team_paths if (('.csv' in item) and (int(item[-8:-4]) > 2006))]
            team_paths = ["./Data/{}/{}/{}".format(self.league, team, item) for item in team_paths]
            df_paths += team_paths
        return df_paths

    def _load_all_team_dfs(self, df_paths):  # Specific Helper load_espn_data
        all_team_dfs = []
        for path in tqdm(df_paths):
            current_df = pd.read_csv(path)
            all_team_dfs.append(current_df)
        return all_team_dfs

    def _add_datetime(self, df):  # Specific Helper load_espn_data
        def add_dt(row):
            return datetime.datetime.strptime(row['Date'], "%B %d, %Y")
        df['datetime'] = df.apply(lambda row: add_dt(row), axis=1)
        df['datetime'] = pd.to_datetime(df['datetime']).apply(lambda x: x.date())
        return df

    def _remove_preseason(self, df):  # Specific Helper load_espn_data
        df = df.loc[df.Week != "HOF"]
        year = str(int(df.Season[0]))
        start_date = self.season_start_dict[year]
        df = df.loc[df.datetime >= start_date]
        return df

    def _clean_concat_team_dfs(self, all_team_dfs):  # Specific Helper load_espn_data
        full_df = pd.concat(all_team_dfs)
        full_df.drop_duplicates(subset="ESPN_ID", inplace=True)
        full_df.sort_values(by="ESPN_ID", inplace=True)
        return full_df

    def load_espn_data(self):  # Top Level
        df_paths = self._get_df_paths()
        all_team_dfs = self._load_all_team_dfs(df_paths)
        all_team_dfs = [self._add_datetime(df) for df in all_team_dfs]
        all_team_dfs = [self._remove_preseason(df) for df in all_team_dfs]
        espn_df = self._clean_concat_team_dfs(all_team_dfs)
        return espn_df

    # def load_espn_data(self):  # Top Level
    #     all_dfs = []
    #     for team in tqdm(self.teams):
    #         df_names = [item for item in os.listdir("./Data/{}/{}/".format(self.league, team))
    #                     if (('.csv' in item) and (int(item[-8:-4]) > 2006))]
    #         for df_name in df_names:
    #             full_path = "./Data/{}/{}/{}".format(self.league, team, df_name)
    #             df = pd.read_csv(full_path)
    #             df = self._remove_preseason(df)
    #             all_dfs.append(df)

    #     full_df = pd.concat(all_dfs)
    #     full_df.drop_duplicates(subset="ESPN_ID", inplace=True)
    #     full_df.sort_values(by="ESPN_ID", inplace=True)
    #     return full_df

    def load_odds_data(self):  # Top Level
        all_dfs = []
        csv_names = [item for item in os.listdir("./Odds/{}".format(self.league)) if '.csv' in item]
        for csv_name in csv_names:
            full_path = "./Odds/{}/{}".format(self.league, csv_name)
            df = pd.read_csv(full_path)
            all_dfs.append(df)

        full_df = pd.concat(all_dfs)
        return full_df

    def convert_odds_teams(self, odds_df):  # Top Level
        def change_name(row):
            return self.odds_conversion_dict[row['Team']]
        odds_df['Team'] = odds_df.apply(lambda row: change_name(row), axis=1)
        return odds_df

    def convert_odds_date(self, odds_df):  # Top Level
        def change_date(row):
            date = str(int(row['Date']))
            month = date[:2] if len(date) == 4 else date[0]
            day = date[-2:]
            dt = datetime.date(int(row['Season']), int(month), int(day))
            return dt
        odds_df['datetime'] = odds_df.apply(lambda row: change_date(row), axis=1)
        odds_df['month'] = odds_df.apply(lambda row: row['datetime'].month, axis=1)
        odds_df['day'] = odds_df.apply(lambda row: row['datetime'].day, axis=1)

        return odds_df

    def _test_row_pair(self, pair):  # Specific Helper game_pairs_from_odds
        row1, row2 = pair
        col_names = ["Season", "Date", "datetime", "month", "day"]
        for name in col_names:
            assert row1[name] == row2[name]

        row1_vh = row1['VH']
        row2_vh = row2['VH']
        if not ((row1_vh == "N") and (row2_vh == "N")):
            assert row1_vh != row2_vh
            assert row1_vh in ["V", "H"]
            assert row2_vh in ["V", "H"]

    def game_pairs_from_odds(self, odds_df):  # Top Level
        game_pairs = []
        rows = [odds_df.iloc[i, :] for i in range(len(odds_df))]
        assert len(rows) % 2 == 0
        for i, row in enumerate(rows):
            if i % 2 == 0:
                current_game = [row]
            else:
                current_game.append(row)
                game_pairs.append(current_game)

        for pair in game_pairs:
            self._test_row_pair(pair)
        return game_pairs

    def _get_line_ou_from_2rows(self, home_row, away_row, col):  # Specific Helper odds_pair_to_dict
        vals = [home_row[col], away_row[col]]
        vals = [float(item) if item != 'pk' else 0.0 for item in vals]
        over_under = max(vals)
        line_val = min(vals)
        home_is_favorite = True if home_row[col] == line_val else False
        home_line = "-" + str(line_val) if home_is_favorite else "+" + str(line_val)
        away_line = "+" + str(line_val) if home_is_favorite else "-" + str(line_val)
        return over_under, home_line, away_line

    def odds_pair_to_dict(self, pair):  # Top Level
        row1, row2 = pair

        home_row = row1 if row1['VH'] in ["H", "N"] else row2
        away_row = row1 if row1['VH'] == 'V' else row2

        open_ou, open_home, open_away = self._get_line_ou_from_2rows(home_row, away_row, col="Open")
        close_ou, close_home, close_away = self._get_line_ou_from_2rows(home_row, away_row, col="Close")
        second_half_ou, second_half_home, second_half_away = self._get_line_ou_from_2rows(home_row, away_row, col="2H")

        result = {
            "Season": int(home_row['Season']),
            "month": home_row['month'],
            "day": home_row['day'],
            "Home": home_row['Team'],
            "Away": away_row['Team'],
            "HQ1": int(home_row['1st']),
            "HQ2": int(home_row['2nd']),
            "HQ3": int(home_row['3rd']),
            "HQ4": int(home_row['4th']),
            "Home_Score": int(home_row['Final']),
            "AQ1": int(away_row['1st']),
            "AQ2": int(away_row['2nd']),
            "AQ3": int(away_row['3rd']),
            "AQ4": int(away_row['4th']),
            "Away_Score": int(away_row['Final']),
            "Home_ML": int(home_row['ML']),
            "Away_ML": int(away_row['ML']),
            "Open_OU": open_ou,
            "Close_OU": close_ou,
            "2H_OU": second_half_ou,
            "Open_Home_Line": open_home,
            "Open_Away_Line": open_away,
            "Close_Home_Line": close_home,
            "Close_Away_Line": close_away,
            "2H_Home_Line": second_half_home,
            "2H_Away_Line": second_half_away
        }
        return result

    def _find_odds_match(self, espn_row, odds_df):  # Specific Helper join_odds_match
        df = copy.deepcopy(odds_df)
        match_cols = ["Season", "month", "day", "Home", "Away", "HQ1", "HQ2", "HQ3", "HQ4", "Home_Score",
                      "AQ1", "AQ2", "AQ3", "AQ4", "Away_Score"]
        for col in match_cols[:5]:
            df = df.loc[df[col] == espn_row[col]]
        return df

    def join_odds_match(self, espn_df, odds_df):  # Top Level
        new_cols = ["Home_ML", "Away_ML"]
        for i in tqdm(range(len(espn_df))):
            pass

    def run(self):  # Run
        espn_df = self.load_espn_data()
        odds_df = self.load_odds_data()
        odds_df = self.convert_odds_teams(odds_df)
        odds_df = self.convert_odds_date(odds_df)
        odds_game_pairs = self.game_pairs_from_odds(odds_df)
        odds_df = pd.DataFrame([self.odds_pair_to_dict(pair) for pair in odds_game_pairs])


if __name__ == "__main__":
    x = Alignment("NFL")
    self = x

    # df_paths = self._get_df_paths()
    # all_team_dfs = self._load_all_team_dfs(df_paths)
    # all_team_dfs = [self._add_datetime(df) for df in all_team_dfs]
    # all_team_dfs = [self._remove_preseason(df) for df in all_team_dfs]

    # espn_df = x.load_espn_data()
    # odds_df = x.load_odds_data()
    # odds_df = x.convert_odds_teams(odds_df)
    # odds_df = x.convert_odds_date(odds_df)
    # pairs = self.game_pairs_from_odds(odds_df)
    # odds_df = pd.DataFrame([x.odds_pair_to_dict(pair) for pair in pairs])
