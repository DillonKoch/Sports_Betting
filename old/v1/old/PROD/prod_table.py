# ==============================================================================
# File: prod_table.py
# Project: PROD
# File Created: Thursday, 18th June 2020 12:48:04 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 1st August 2020 3:09:18 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Program to create and update the season PROD table for each league
# As new data from ESPN, odds, ESB odds are available, this will update the prod csv
# ==============================================================================

import copy
import datetime
import json
import os
import sys
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Utility.Utility import listdir_fullpath, parse_league


class Prod_Table:
    """
    class for creating PROD table for each of the four leagues, using data from ESPN, Odds, ESB
    """

    def __init__(self, league: str):
        self.league = league
        self.prod_table = ROOT_PATH + "/PROD/PROD_{}.csv".format(self.league)
        self.esb_table = ROOT_PATH + "/ESB_Data/{}/Game_Lines.csv".format(self.league)
        self.config_file = ROOT_PATH + "/PROD/{}_prod.json".format(self.league.lower())
        self.teams = os.listdir(ROOT_PATH + "/ESPN_Data/{}/".format(self.league))

    @property
    def config(self):  # Property
        with open(self.config_file) as f:
            config = json.load(f)
        return config

    @property
    def season_start_dict(self):  # Property
        config_dict = self.config['season_start_dates']
        years = [str(item) for item in range(2007, 2021)]
        dic = {year: datetime.date(config_dict[year][0], config_dict[year][1], config_dict[year][2]) for year in years}
        return dic

    @property
    def odds_name_conversions(self):  # Property
        return self.config["team_name_conversion_dict"]

    def _get_espn_dfs(self):  # Specific Helper load_espn_data
        """
        loads each team's csv from ESPN_Data folder
        """
        df_paths = listdir_fullpath(ROOT_PATH + "/ESPN_Data/{}/".format(self.league))
        df_paths = [item for item in df_paths if ('.csv' in item)]
        dfs = [pd.read_csv(path) for path in tqdm(df_paths)]
        return dfs

    def _clean_concat_team_dfs(self, all_team_dfs):  # Specific Helper load_espn_data  Tested
        """
        merges all team's dfs together into one df with all games in the league since 2007
        need to drop duplicates because each game appears in both team's df
        """
        full_df = pd.concat(all_team_dfs)
        full_df.drop_duplicates(subset="ESPN_ID", inplace=True)
        full_df.sort_values(by="datetime", inplace=True)
        full_df = full_df.loc[:, self.config["ESPN_cols"]]
        full_df['datetime'] = pd.to_datetime(full_df['datetime']).apply(lambda x: x.date())
        return full_df

    def load_espn_data(self):  # Top Level  Tested
        """
        creates a df with all main espn data in a league (and datetime)
        """
        all_team_dfs = self._get_espn_dfs()
        espn_df = self._clean_concat_team_dfs(all_team_dfs)
        return espn_df

    def _load_odds_data(self):
        """
        creates one df with all odds data for the given league
        """
        df_paths = listdir_fullpath(ROOT_PATH + "/Odds/{}/".format(self.league))
        df_paths = [path for path in df_paths if '.csv' in path]
        dfs = [pd.read_csv(path) for path in tqdm(df_paths)]
        full_df = pd.concat(dfs)
        return full_df

    def convert_odds_teams(self, odds_df):  # Top Level Tested
        """
        changes the odds team names to match the ESPN data
        - e.g. change "Minnesota" to "Minnesota Vikings" to make merging easier
        - if no different name is given in json file, the current name is kept
        """
        def change_name(row):
            name = self.odds_name_conversions[row['Team']]
            return name if name != "" else row['Team']
        odds_df['Team'] = odds_df.apply(lambda row: change_name(row), axis=1)
        return odds_df

    def convert_odds_date(self, odds_df):  # Top Level  Tested
        """
        creates "datetime" column in odds_df in the same format as ESPN data
        """
        def change_date(row):
            date = str(int(row['Date']))
            month = date[:2] if len(date) == 4 else date[0]
            day = date[-2:]
            season_year = str(int(row['Season']))
            season_start_date = self.season_start_dict[season_year]
            year = season_year if int(month) >= season_start_date.month else int(season_year) + 1
            dt = datetime.date(int(year), int(month), int(day))
            return dt
        odds_df['datetime'] = odds_df.apply(lambda row: change_date(row), axis=1)
        odds_df['datetime'] = pd.to_datetime(odds_df['datetime']).apply(lambda x: x.date())
        return odds_df

    def _test_row_pair(self, pair):  # QA Testing game_pairs_from_odds
        """
        performs some QA testing on each pair of rows from the odds data
        makes sure the two rows are referring to the same game and match up
        """
        row1, row2 = pair
        col_names = ["Season", "Date", "datetime"]
        for name in col_names:
            try:
                assert row1[name] == row2[name]
            except BaseException:
                # print(row1, row2)
                print(name)

        row1_vh = row1['VH']
        row2_vh = row2['VH']
        if not ((row1_vh == "N") and (row2_vh == "N")):
            try:
                assert row1_vh != row2_vh
                assert row1_vh in ["V", "H"]
                assert row2_vh in ["V", "H"]
            except BaseException:
                print(row1, row2)

    def game_pairs_from_odds(self, odds_df):  # Top Level  Tested
        """
        returns a list of games from the odds df - each list includes
        two rows from the odds df, since that's how the data is presented
        """
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

    def duplicate_game_pairs(self, game_pairs):
        new_game_pairs = []
        game_pairs_copy = copy.deepcopy(game_pairs)
        for pair in tqdm(game_pairs_copy):
            g1, g2 = pair
            g1['VH'] = "H"
            g2['VH'] = "V"
            new_game_pairs.append([g1, g2])

            g1_copy = copy.deepcopy(g1)
            g1_copy['VH'] = "V"
            g2_copy = copy.deepcopy(g2)
            g2_copy['VH'] = "H"
            new_game_pairs.append([g1_copy, g2_copy])
        return game_pairs + new_game_pairs

    def _get_line_ou_from_2rows(self, home_row, away_row, col):  # Specific Helper odds_pair_to_dict
        """
        returns the over under, home/away line from two rows of the odds data
        if either line/over under is "NL", some logic is used to determine if the value
        is the line or over under
        """
        home_val = "nl" if isinstance(home_row[col], float) else home_row[col].lower() if home_row[col].lower() != "pk" else '0.0'
        away_val = "nl" if isinstance(away_row[col], float) else away_row[col].lower() if away_row[col].lower() != "pk" else '0.0'
        no_line_count = [home_val, away_val].count("nl")
        if no_line_count == 2:
            return "nl", "nl", "nl"
        elif no_line_count == 1:
            if self.league == "NFL":
                raise ValueError("ERROR: NL found for an NFL game")
            non_nl_val = [item for item in [home_val, away_val] if item != "nl"][0]
            if self.league == "NCAAF":
                home_line = "nl"
                away_line = "nl"
                over_under = "nl"
            elif float(non_nl_val) < self.config["{}_cutoff".format(col)]:
                home_is_favorite = True if home_val == non_nl_val else False
                if home_is_favorite:
                    home_line = "-" + str(float(home_val))
                    away_line = "+" + str(float(home_val))
                    over_under = "nl"
                else:
                    home_line = "+" + str(float(away_val))
                    away_line = "-" + str(float(away_val))
                    over_under = "nl"
            else:
                home_line = "nl"
                away_line = "nl"
                over_under = non_nl_val

        else:
            home_is_favorite = True if float(home_val) < float(away_val) else False
            if home_is_favorite:
                home_line = "-" + str(float(home_val))
                away_line = "+" + str(float(home_val))
                over_under = away_val
            else:
                home_line = "+" + str(float(away_val))
                away_line = "-" + str(float(away_val))
                over_under = home_val
        return over_under, home_line, away_line

    def odds_pair_to_dict(self, pair):  # Top Level
        """
        takes an odds pair (two rows from odds data) and creates a dictionary
        with all the information from the two rows
        - this presents all the information for a game in an easily merge-able way
        """
        row1, row2 = pair

        home_row = row1 if row1['VH'] in ["H", "N"] else row2
        away_row = row1 if row1['VH'] == 'V' else row2

        open_ou, open_home, open_away = self._get_line_ou_from_2rows(home_row, away_row, col="Open")
        close_ou, close_home, close_away = self._get_line_ou_from_2rows(home_row, away_row, col="Close")
        second_half_ou, second_half_home, second_half_away = self._get_line_ou_from_2rows(home_row, away_row, col="2H")

        result = {
            "Season": int(home_row['Season']),
            "datetime": home_row['datetime'],
            "Home": home_row['Team'],
            "Away": away_row['Team'],
            "Home_Score": int(home_row['Final']),
            "Away_Score": int(away_row['Final']),
            "Home_ML": home_row['ML'],
            "Away_ML": away_row['ML'],
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
        if self.league != "NCAAB":
            quarters_dict = {
                "HQ1": int(home_row['1st']),
                "HQ2": int(home_row['2nd']),
                "HQ3": int(home_row['3rd']),
                "HQ4": int(home_row['4th']),
                "AQ1": int(away_row['1st']),
                "AQ2": int(away_row['2nd']),
                "AQ3": int(away_row['3rd']),
                "AQ4": int(away_row['4th'])}
            result = dict(list(result.items()) + list(quarters_dict.items()))
        else:
            halves_dict = {
                "H1H": int(home_row['1st']),
                "H2H": int(home_row['2nd']),
                "A1H": int(away_row['1st']),
                "A2H": int(away_row['2nd'])}
            result = dict(list(result.items()) + list(halves_dict.items()))

        return result

    def merge_espn_odds(self, espn_df, odds_df):  # Top Level
        """
        merges espn data and odds data on datetime, home, away columns
        """
        odds_df['datetime'] = pd.to_datetime(odds_df['datetime']).apply(lambda x: x.date())
        merge_cols = ["datetime", "Home", "Away"]
        df = espn_df.merge(odds_df, on=merge_cols, how="left")

        final_cols = self.config["ESPN_cols"]
        final_cols = [item if item not in ["Season", "Home_Score", "Away_Score"]
                      else item + "_x" for item in final_cols]
        final_cols = [item for item in final_cols if item not in
                      ["HQ1", "HQ2", "HQ3", "HQ4", "AQ1", "AQ2", "AQ3", "AQ4", "H1H", "H2H", "A1H", "A2H", "HOT", "AOT"]]

        if self.league != "NCAAB":
            final_cols += ['HQ1_x', 'HQ2_x', 'HQ3_x', 'HQ4_x', "HOT", "AQ1_x", "AQ2_x", "AQ3_x", "AQ4_x", "AOT"]
        else:
            final_cols += ["H1H_x", "H2H_x", "HOT", "A1H_x", "A2H_x", "AOT"]

        final_cols += ["Home_ML", "Away_ML", "Open_OU", "Close_OU", "2H_OU", "Open_Home_Line",
                       "Open_Away_Line", "Close_Home_Line", "Close_Away_Line", "2H_Home_Line",
                       "2H_Away_Line"]

        return df.loc[:, final_cols]

    def add_odds_data(self, espn_df):  # Top Level
        """
        runs odds data methods and joins result to espn data
        """
        odds_df = self._load_odds_data()
        odds_df = self.convert_odds_teams(odds_df)
        odds_df = self.convert_odds_date(odds_df)
        game_pairs = self.game_pairs_from_odds(odds_df)
        game_pairs = self.duplicate_game_pairs(game_pairs)
        odds_df = pd.DataFrame([self.odds_pair_to_dict(pair) for pair in tqdm(game_pairs)])
        df = self.merge_espn_odds(espn_df, odds_df)
        return df

    def add_esb_data(self, df):  # Top Level
        """
        merges Elite Sportsbook data to the espn/odds dataframe
        """
        esb_df = pd.read_csv(self.esb_table)
        esb_df['datetime'] = pd.to_datetime(esb_df['datetime']).apply(lambda x: x.date())
        esb_df = esb_df.drop_duplicates(subset=["Home", "Away", "datetime"], keep="last")
        df = df.merge(esb_df, on=["datetime", "Home", "Away"], how="left")
        return df

    def prod_table_from_scratch(self):  # Run
        df = self.load_espn_data()
        df = self.add_odds_data(df)
        df = self.add_esb_data(df)
        df = df.drop_duplicates(subset=["Home", "Away", "datetime"], keep="last")
        df.to_csv(ROOT_PATH + "/PROD/{}_PROD.csv".format(self.league), index=False)
        return df

    def espn_odds_non_matches(self):  # QA Testing
        """
        displays a df of ESPN games with no match from odds data - goal is to get an empty df
        """
        espn_df = self.load_espn_data()
        merged_df = self.add_odds_data(espn_df)
        no_match = merged_df.loc[merged_df.Away_ML.isnull()]
        no_match = no_match.loc[no_match.datetime < datetime.date.today()]
        no_match.to_csv("no_match_{}.csv".format(self.league), index=False)
        return no_match


if __name__ == "__main__":
    league = parse_league()
    x = Prod_Table(league)
    x.prod_table_from_scratch()
    # nfl = Prod_Table("NFL")
    # nba = Prod_Table("NBA")
    # ncaaf = Prod_Table("NCAAF")
    # ncaab = Prod_Table("NCAAB")
    # self = nba
    # df = self.prod_table_from_scratch()
    # # ndf = self.espn_odds_non_matches()