# ==============================================================================
# File: modeling_data.py
# Project: allison
# File Created: Tuesday, 23rd November 2021 9:14:48 pm
# Author: Dillon Koch
# -----
# Last Modified: Tuesday, 23rd November 2021 9:14:49 pm
# Modified By: Dillon Koch
# -----
#
# -----
# building the final df for modeling with avg past stats, and optinoal player stats
# ==============================================================================

import concurrent.futures
import datetime
import json
import os
import sys
import warnings
from os.path import abspath, dirname

import pandas as pd
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from Data_Cleaning.player_data import Player_Data

warnings.filterwarnings("ignore")


def multithread(func, func_args):  # Multithreading
    with concurrent.futures.ThreadPoolExecutor() as executor:
        result = list(tqdm(executor.map(func, func_args), total=len(func_args)))
    return result


class Modeling_Data:
    def __init__(self, league):
        self.league = league
        self.player_data = Player_Data(league)
        self.base_df, self.game_dicts = self.load_base_df_dicts()
        self.game_dicts_new_to_old = self.game_dicts[::-1]

        # * loading ESPN Teams JSON
        with open(ROOT_PATH + f"/Data/Teams/{self.league}_Teams.json", 'r') as f:
            self.teams_dict = json.load(f)
        self.json_teams = list(self.teams_dict['Teams'].keys())

        # * loading roster df
        self.roster_df = pd.read_csv(ROOT_PATH + f"/Data/ESPN/{self.league}/Rosters.csv")
        self.roster_teams = list(set(list(self.roster_df['Team'])))

        # * making lists of df columns
        self.feature_cols = self.get_feature_cols()
        self.betting_cols = ['Home_Line_Close', 'Home_Line_Close_ML', 'OU_Close', 'OU_Close_ML',
                             'Home_ML', 'Away_ML']
        self.targets = ['Home_Covered', 'Home_Win', 'Over_Covered']
        self.all_df_cols = ['Home', 'Away', 'Date'] + self.betting_cols + self.targets + self.feature_cols

    def _clean_base_df(self, df):  # Specific Helper load_base_df_dicts
        """
        cleaning up the df before it's broken up into dicts
        """
        # * splitting into games that are final/not
        final_df = df[df['Final_Status'].notnull()]
        non_final_df = df[df['Final_Status'].isnull()]

        # * cleaning the final_df values
        final_df['HOT'].fillna(0, inplace=True)
        final_df['AOT'].fillna(0, inplace=True)
        final_df.replace("--", None, inplace=True)

        # * merging the datasets back together, sorting, resetting index
        full_df = pd.concat([final_df, non_final_df])
        full_df.sort_values(by=['Date', 'Home', 'Away'], inplace=True)
        full_df.reset_index(inplace=True, drop=True)
        return full_df

    def _target_feature_engineering(self, df):  # Specific Helper load_base_df_dicts
        """
        Engineering new target features to be modeled for each bet type
        """
        # * Spread - Home_Covered
        df['Home_Covered'] = (df['Home_Final'] + df['Home_Line_Close']) > df['Away_Final']
        df['Home_Covered'] = df['Home_Covered'].astype(int)
        # * MoneyLine - Home_Win
        df['Home_Win'] = df['Home_Final'] > df['Away_Final']
        df['Home_Win'] = df['Home_Win'].astype(int)
        # * Total: Over_Covered
        df['Over_Covered'] = (df['Home_Final'] + df['Away_Final']) > df['OU_Close']
        df['Over_Covered'] = df['Over_Covered'].astype(int)

        for col in ['Home_Win', 'Home_Covered', 'Over_Covered']:
            df.loc[df['Final_Status'].isnull(), col] = None
        return df

    def load_base_df_dicts(self):  # Top Level INIT
        """
        loading the base df, cleaning it, engineering targets, and arranging into dict form
        """
        df = pd.read_csv(ROOT_PATH + f"/Data/{self.league}.csv")
        df = self._clean_base_df(df)
        df = self._target_feature_engineering(df)
        game_dicts = [{col: val for col, val in zip(list(df.columns), df_row)} for df_row in df.values.tolist()]
        return df, game_dicts

    def _quarters_halves_final_features(self):  # Specific Helper get_feature_cols
        """
        making a list of the quarters/halves features (halves for NCAAB only)
        """
        overtimes = ['HOT', 'AOT']
        finals = ['Home_Final', 'Away_Final']
        halves = ['H1H', 'H2H', 'A1H', 'A2H'] + overtimes + finals
        quarters = ['H1Q', 'H2Q', 'H3Q', 'H4Q', 'A1Q', 'A2Q', 'A3Q', 'A4Q'] + overtimes + finals
        halves += [item + "_Allowed" for item in halves]
        quarters += [item + "_Allowed" for item in quarters]
        return halves if self.league == "NCAAB" else quarters

    def _wrap_home_away_allowed(self, stat_list):  # Helping Helper _game_stats_features
        """
        wrapping the stat_list features with Home/Away to start, and Allowed to end
        """
        home = ['Home_' + stat for stat in stat_list]
        away = ['Away_' + stat for stat in stat_list]
        home_allowed = [stat + '_Allowed' for stat in home]
        away_allowed = [stat + '_Allowed' for stat in away]
        return home + home_allowed + away + away_allowed

    def _game_stats_features(self):  # Specific Helper get_feature_cols
        """
        returning a list of team stats for the given league
        """
        nfl_stats = ['1st_Downs', 'Passing_1st_downs', 'Rushing_1st_downs', '1st_downs_from_penalties',
                     'Total_Plays', 'Total_Yards', 'Total_Drives', 'Yards_per_Play', 'Passing',
                     'Yards_per_pass', 'Interceptions_thrown', 'Rushing', 'Rushing_Attempts',
                     'Yards_per_rush', 'Turnovers', 'Fumbles_lost', 'Defensive_Special_Teams_TDs',
                     '3rd_downs_converted', '3rd_downs_total', '4th_downs_converted', '4th_downs_total',
                     'Passes_completed', 'Passes_attempted', 'Sacks', 'Sacks_Yards_Lost',
                     'Red_Zone_Conversions', 'Red_Zone_Trips', 'Penalties', 'Penalty_Yards', 'Possession']
        ncaaf_stats = ['1st_Downs',
                       'Total_Yards', 'Passing', 'Yards_per_pass', 'Interceptions_thrown', 'Rushing',
                       'Rushing_Attempts', 'Yards_per_rush', 'Turnovers', 'Fumbles_lost',
                       '3rd_downs_converted', '3rd_downs_total', '4th_downs_converted', '4th_downs_total',
                       'Passes_completed', 'Passes_attempted', 'Penalties', 'Penalty_Yards', 'Possession']
        nba_stats = ['Field_Goal_pct', 'Three_Point_pct', 'Free_Throw_pct', 'Rebounds', 'Offensive_Rebounds',
                     'Defensive_Rebounds', 'Assists', 'Steals', 'Blocks', 'Total_Turnovers', 'Points_Off_Turnovers',
                     'Fast_Break_Points', 'Points_in_Paint', 'Fouls', 'Technical_Fouls', 'Flagrant_Fouls',
                     'Largest_Lead', 'FG_made', 'FG_attempted', '3PT_made', '3PT_attempted', 'FT_made',
                     'FT_attempted']
        ncaab_stats = ['Field_Goal_pct', 'Three_Point_pct', 'Free_Throw_pct', 'Rebounds', 'Offensive_Rebounds',
                       'Defensive_Rebounds', 'Assists', 'Steals', 'Blocks', 'Total_Turnovers', 'Fouls',
                       'Technical_Fouls', 'Flagrant_Fouls', 'Largest_Lead', 'FG_made', 'FG_attempted',
                       '3PT_made', '3PT_attempted', 'FT_made', 'FT_attempted']
        stat_dict = {"NFL": self._wrap_home_away_allowed(nfl_stats), "NBA": self._wrap_home_away_allowed(nba_stats),
                     "NCAAF": self._wrap_home_away_allowed(ncaaf_stats), "NCAAB": self._wrap_home_away_allowed(ncaab_stats)}
        return stat_dict[self.league]

    def get_feature_cols(self):  # Top Level  INIT
        """
        loading all the feature cols for the given league
        """
        quarters_halves_final = self._quarters_halves_final_features()
        game_stats = self._game_stats_features()
        return quarters_halves_final + game_stats

    def load_modeling_df(self, num_past_games, player_stats):  # Top Level
        """
        loading the existing modeling_df if it exists, else making a new one
        """
        ps_str = "" if player_stats else "no_"
        path = ROOT_PATH + f"/Data/Modeling_Data/{self.league}/{ps_str}player_stats_avg_{num_past_games}_past_games.csv"
        if os.path.exists(path):
            df = pd.read_csv(path)
        else:
            df = pd.DataFrame(columns=self.all_df_cols)
        return df

    def get_no_update_modeling_df(self, modeling_df):
        """
        subsetting the modeling_df into rows that are already fully built
        """
        no_update_df = modeling_df[~pd.isnull(modeling_df[self.betting_cols + self.targets]).any(axis=1)]
        no_update_df.reset_index(inplace=True, drop=True)
        return no_update_df

    def get_update_home_away_dates(self, modeling_df, days_since):
        """
        creating lists of (home, away, date) for games that need to be updated
        - games needing updates have a missing betting/target val or have not been played yet
        - non-played games are updated so the avg stats are fresh
        - not all of these will make it past self.get_update_game_dicts() (like first game w/ no past avg stats)
        """
        # * missing val in existing modeling_df
        update_modeling_df = modeling_df[pd.isnull(modeling_df[self.betting_cols + self.targets]).any(axis=1)]
        past_date = (datetime.datetime.now() - datetime.timedelta(days=days_since)).strftime('%Y-%m-%d')
        update_modeling_df = update_modeling_df[update_modeling_df['Date'] >= past_date]
        update_home_away_dates = [(row['Home'], row['Away'], row['Date']) for i, row in update_modeling_df.iterrows()]

        # * games not in modeling_df (but in /Data/{league}.csv)
        modeling_df_home_away_dates = [(row['Home'], row['Away'], row['Date']) for i, row in modeling_df.iterrows()]
        missing_game_dicts = [gd for gd in self.game_dicts if (gd['Home'], gd['Away'], gd['Date']) not in modeling_df_home_away_dates]
        missing_home_away_dates = [(mgd['Home'], mgd['Away'], mgd['Date']) for mgd in missing_game_dicts]
        missing_home_away_dates = [mhad for mhad in missing_home_away_dates if mhad[2] > past_date]
        return update_home_away_dates + missing_home_away_dates

    def _team_eligible_date(self, team, num_past_games):  # Specific Helper get_update_game_dicts
        """
        finding the date AFTER which a team has enough previous games to compute avg's
        """
        count = 0
        for i, game_dict in enumerate(self.game_dicts):
            home = game_dict['Home']
            away = game_dict['Away']
            if team in [home, away]:
                count += 1
            if count == num_past_games:
                return game_dict['Date']
        return "999999-12-31"

    def get_update_game_dicts(self, update_home_away_dates, num_past_games, days_out=5):  # Top Level
        """
        - teams are in the ESPN teams json file
        - teams have enough previous games to compute avg stats
        - games that are not played yet ARE ALLOWED
        - games being played within the next 'days_out' days
        """
        # * filtering on teams being in the ESPN teams json file
        update_home_away_dates = [uhad for uhad in update_home_away_dates
                                  if ((uhad[0] in self.json_teams) and (uhad[1] in self.json_teams))]

        # * filtering on teams having a roster scraped
        update_home_away_dates = [uhad for uhad in update_home_away_dates
                                  if ((uhad[0] in self.roster_teams) and (uhad[1] in self.roster_teams))]

        # * filtering based on date of teams' eligibility
        team_eligible_dates = {team: self._team_eligible_date(team, num_past_games) for team in self.json_teams}
        update_home_away_dates = [uhad for uhad in update_home_away_dates if (uhad[2] > team_eligible_dates[uhad[0]])
                                  and ((uhad[2] > team_eligible_dates[uhad[1]]))]

        # * filtering on days_out
        future_date = (datetime.datetime.now() + datetime.timedelta(days=days_out)).strftime('%Y-%m-%d')
        update_home_away_dates = [uhad for uhad in update_home_away_dates if uhad[2] <= future_date]

        # * getting the game_dicts
        update_game_dicts = [gd for gd in self.game_dicts if (gd['Home'], gd['Away'], gd['Date']) in update_home_away_dates]
        return update_game_dicts

    def _query_recent_games(self, team, date, num_past_games):  # Helping Helper _build_update_df_row_dict
        """
        finding recent game_dicts for a team before a given date
        """
        recent_games = []
        for game_dict in self.game_dicts_new_to_old:
            if game_dict['Date'] >= date:
                continue

            if 'Final' not in str(game_dict['Final_Status']):
                continue

            home = game_dict['Home']
            away = game_dict['Away']
            if team in [home, away]:
                recent_games.append(game_dict)
            if len(recent_games) == num_past_games:
                return recent_games
        raise ValueError(f"DID NOT FIND ENOUGH GAMES for {team} on {date} with {num_past_games} past games")

    def _get_opp_feature_col(self, feature_col, home_feature):  # Helping Helper _avg_feature_col
        opp_feature_col = feature_col.replace("Home", "Away") if home_feature else feature_col.replace("Away", "Home")
        opp_feature_col = 'A' + opp_feature_col[1:] if home_feature else 'H' + opp_feature_col[1:]
        return opp_feature_col

    def _avg_feature_col(self, feature_col, home, away, home_recent_games, away_recent_games):  # Helping Helper _build_update_df_row_dict
        """
        Computing the average value of 'feature_col' in recent games
        - inspects home/away recent games based on name of feature_col
        """
        allowed_feature = "Allowed" in feature_col
        feature_col = feature_col.replace("_Allowed", "")
        home_feature = True if feature_col[0] == 'H' else False
        recent_games = home_recent_games if home_feature else away_recent_games
        team = home if home_feature else away

        opp_feature_col = self._get_opp_feature_col(feature_col, home_feature)
        home_feature_col = feature_col if home_feature else opp_feature_col
        away_feature_col = opp_feature_col if home_feature else feature_col

        # * if we're looking for an allowed, stat, we're just looking for the opposite col
        if allowed_feature:
            home_feature_col, away_feature_col = away_feature_col, home_feature_col

        vals = []
        for recent_game_dict in recent_games:
            team_is_home = True if recent_game_dict['Home'] == team else False
            new_val = recent_game_dict[home_feature_col] if team_is_home else recent_game_dict[away_feature_col]
            vals.append(float(new_val))

        return round(sum(vals) / len(vals), 2)

    def _add_targets_bet_cols(self, row_dict, update_game_dict):  # Helping Helper _build_update_df_row_dict
        """
        adding targets and betting columns to the final df straight from the merged df
        - these are not averaged across past games like the other features
        """
        for target in self.targets + self.betting_cols:
            row_dict[target] = update_game_dict[target]
        return row_dict

    def _build_update_df_row_dict(self, args):  # Specific Helper build_update_modeling_df
        update_game_dict, num_past_games = args
        home, away, date = update_game_dict['Home'], update_game_dict['Away'], update_game_dict['Date']
        home_recent_games = self._query_recent_games(home, date, num_past_games)
        away_recent_games = self._query_recent_games(away, date, num_past_games)

        # * feature cols
        row_dict = {feature_col: self._avg_feature_col(feature_col, home, away, home_recent_games, away_recent_games)
                    for feature_col in self.feature_cols}

        # * home, away, date
        row_dict['Home'] = update_game_dict['Home']
        row_dict['Away'] = update_game_dict['Away']
        row_dict['Date'] = update_game_dict['Date']

        # * targets and betting cols
        row_dict = self._add_targets_bet_cols(row_dict, update_game_dict)
        return row_dict

    def _add_player_stats(self, update_modeling_df, update_game_dicts):  # Specific Helper build_update_modeling_df
        """
        adding several more columns to the df with all the player stats
        """
        home_teams = [ugd['Home'] for ugd in update_game_dicts]
        away_teams = [ugd['Away'] for ugd in update_game_dicts]
        dates = [ugd['Date'] for ugd in update_game_dicts]

        new_df_cols = ["H" + item for item in self.player_data.feature_col_names] + ['A' + item for item in self.player_data.feature_col_names]
        new_df = pd.DataFrame(columns=new_df_cols)

        def run_player_data(args):
            team, date = args
            return self.player_data.run(team, date)

        home_inputs = [(home_team, date) for home_team, date in zip(home_teams, dates)]
        home_stats = multithread(run_player_data, home_inputs)
        away_inputs = [(away_team, date) for away_team, date in zip(away_teams, dates)]
        away_stats = multithread(run_player_data, away_inputs)

        for i, (home_stat, away_stat) in enumerate(zip(home_stats, away_stats)):
            new_df.loc[len(new_df)] = home_stat + away_stat

        final_df = pd.concat([update_modeling_df, new_df], axis=1)
        return final_df

    def fill_na_values(self, df):  # Specific Helper build_update_modeling_df
        """
        simple mean-imputation for missing values in feature columns
        """
        for feature_col in self.feature_cols:
            df[feature_col].fillna(value=df[feature_col].mean(), inplace=True)
        return df

    def build_update_modeling_df(self, update_game_dicts, num_past_games, player_stats):  # Top Level
        """
        using the update_game_dicts to build out a df with those games' values
        # optionally adding player stats
        """
        args = [(ugd, num_past_games) for ugd in update_game_dicts]
        update_df_row_dicts = multithread(self._build_update_df_row_dict, args)
        update_modeling_df = pd.DataFrame(update_df_row_dicts, columns=self.all_df_cols)
        if player_stats:
            update_modeling_df = self._add_player_stats(update_modeling_df, update_game_dicts)
        update_modeling_df = self.fill_na_values(update_modeling_df)
        print(f"Updating {len(update_modeling_df)} games...")
        return update_modeling_df

    def run(self, num_past_games, player_stats, days_since=10, days_out=10):  # Run
        modeling_df = self.load_modeling_df(num_past_games, player_stats)
        full_df = self.get_no_update_modeling_df(modeling_df)  # no missing betting odds/targets
        update_home_away_dates = self.get_update_home_away_dates(modeling_df, days_since)  # had's of games that need to be updated
        update_game_dicts = self.get_update_game_dicts(update_home_away_dates, num_past_games, days_out)
        while len(update_game_dicts) > 0:
            games_per_iter = 2000
            current_ugds = update_game_dicts[:games_per_iter]
            update_game_dicts = update_game_dicts[games_per_iter:]

            update_modeling_df = self.build_update_modeling_df(current_ugds, num_past_games, player_stats)
            full_df = pd.concat([full_df, update_modeling_df])
            full_df.reset_index(inplace=True, drop=True)
            full_df.sort_values(by=['Date', 'Home', 'Away'], inplace=True)

            # * saving the df
            ps_str = "" if player_stats else "no_"
            path = ROOT_PATH + f"/Data/Modeling_Data/{self.league}/{ps_str}player_stats_avg_{num_past_games}_past_games.csv"
            full_df.to_csv(path, index=False)
            print(f"{len(full_df)} rows SAVED!")
            print(f"{len(update_game_dicts)} games to update left")

    def run_all(self):  # Run
        """
        runs through all the num past games with and without player stats
        """
        for npg in [3, 5, 10, 15, 20, 25]:
            for ps in [True, False]:
                print(f"{self.league}, {npg} past games, player stats: {ps}")
                days_out = 14 if league != "NCAAF" else 50
                self.run(npg, ps, days_since=14, days_out=days_out)


if __name__ == '__main__':
    for league in ['NFL', 'NBA', 'NCAAF']:
        # for league in ['NCAAB']:
        # ! be sure to check on 'days_since' and 'days_out'
        x = Modeling_Data(league)
        x.run_all()
