# ==============================================================================
# File: player_data.py
# Project: allison
# File Created: Sunday, 31st October 2021 2:55:59 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 31st October 2021 2:56:00 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Cleaning/combining player data to be fed into models
# ==============================================================================


import datetime
import json
import sys
from os.path import abspath, dirname

import numpy as np
import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class Player_Data:
    def __init__(self, league):
        self.league = league
        self.football_league = league in ['NFL', 'NCAAF']

        # * loading data
        self.player_stats_df = self.load_clean_player_stats_df()
        self.player_stats_lists = self.player_stats_df.values.tolist()
        self.player_stats_features = list(self.player_stats_df.columns)
        self.player_df = pd.read_csv(f"{ROOT_PATH}/Data/ESPN/{self.league}/Players.csv")
        self.roster_df = pd.read_csv(f"{ROOT_PATH}/Data/ESPN/{self.league}/Rosters.csv")
        self.injury_df = pd.read_csv(f"{ROOT_PATH}/Data/Covers/{self.league}/Injuries.csv")
        with open(ROOT_PATH + f"/Data/Covers/{self.league}/Player_Matches.json", 'r') as f:
            self.player_matches = json.load(f)

        # * Positions for each team
        self.football_positions = ['QB', 'RB', 'WR', 'TE', 'DT', 'DE', 'LB', 'CB', 'S', 'K', 'P']
        self.football_pos_dict = {'Quarterback': 'QB', 'Running Back': 'RB', 'Wide Receiver': 'WR',
                                  'Tight End': 'TE', 'Nose Tackle': 'DT', 'Defensive Tackle': 'DT', 'Defensive End': 'DE',
                                  'Linebacker': 'LB', 'Cornerback': 'CB', 'Free Safety': 'S', 'Defensive Back': 'S',
                                  'Strong Safety': 'S', 'Safety': 'S', 'Place Kicker': 'K', 'Punter': 'P'}
        self.football_pos_num_dict = {"QB": 2, "RB": 2, "WR": 4, "TE": 2, "DT": 3, "DE": 3, "LB": 4, "CB": 3, "S": 3, "K": 1, "P": 1}

        self.basketball_positions = ["PG", "SG", "SF", "PF", "C"]
        self.basketball_pos_dict = {"Point Guard": "PG", "Shooting Guard": "SG", "Guard": "SG", "Small Forward": "SF",
                                    "Forward": "SF", "Power Forward": "PF", "Center": "C"}
        self.basketball_pos_num_dict = {"PG": 2, "SG": 2, "SF": 2, "PF": 2, "C": 2}

        self.positions = self.football_positions if self.football_league else self.basketball_positions
        self.pos_dict = self.football_pos_dict if self.football_league else self.basketball_pos_dict
        self.rev_pos_dict = {v: k for k, v in self.pos_dict.items()}
        self.pos_num_dict = self.football_pos_num_dict if self.football_league else self.basketball_pos_num_dict

        # * stats we care about for each position
        qb_stats = ['Passing_Comp_Att_s1', 'Passing_Comp_Att_s2', 'Passing_Yards', 'Avg_Yards_per_Pass',
                    'Passing_Touchdowns', 'Interceptions_Thrown', 'Times_Sacked_d1', 'Times_Sacked_d2',
                    'QBR', 'Passer_Rating', 'Carries', 'Rushing_Yards', 'Avg_Yards_per_Rush',
                    'Rushing_Touchdowns', 'Longest_Rush', 'Fumbles', 'Fumbles_Lost', 'Fumbles_Recovered']
        rb_stats = qb_stats[-8:]
        wr_stats = ['Receptions', 'Receiving_Yards', 'Yards_per_Catch', 'Receiving_Touchdowns', 'Longest_Reception',
                    'Targets', 'Fumbles', 'Fumbles_Lost', 'Fumbles_Recovered']
        te_stats = wr_stats
        dt_stats = ['Fumbles_Recovered', 'Tackles', 'Solo_Tackles', 'Sacks', 'Tackles_for_Loss',
                    'QB_Hurries', 'Passes_Defended', 'QB_Hits', 'Touchdowns', 'Interceptions_Caught',
                    'Interception_Return_Yards', 'Pick_Sixes']
        de_stats = dt_stats
        lb_stats = dt_stats
        cb_stats = dt_stats
        s_stats = dt_stats
        k_stats = ['FG_Made_Att_s1', 'FG_Made_Att_s2', 'FG_Pct', 'Longest_Field_Goal', 'XP_Made_Att_s1',
                   'XP_Made_Att_s2', 'Kicking_Points']
        p_stats = ['Punts', 'Punt_Yards', 'Touchbacks', 'Punts_Inside_20', 'Longest_Punt']
        football_position_stats = [qb_stats, rb_stats, wr_stats, te_stats, dt_stats, de_stats, lb_stats, cb_stats, s_stats, k_stats, p_stats]
        self.football_stat_dict = {pos: stats for pos, stats in zip(self.football_positions, football_position_stats)}

        self.basketball_stats = ["Minutes", "FG_d1", "FG_d2", "3PT_d1", "3PT_d2", "FT_d1", "FT_d2", "Offensive_Rebounds", "Defensive_Rebounds",
                                 "Total_Rebounds", "Assists", "Steals", "Blocks", "Turnovers", "Fouls", "Plus_Minus", "Points"]
        self.basketball_stat_dict = {pos: self.basketball_stats for pos in self.basketball_positions}
        self.pos_stat_dict = self.football_stat_dict if self.football_league else self.basketball_stat_dict

        # * dict for converting injury first word to numeric status
        self.status_fw_to_num_dict = {"i-r": 0, "out": 0, "early": 0, "mid": 0, "late": 0, "doub": 1, "ques": 2, "quest": 2, "-": 2,
                                      "day-to-day": 2, "prob": 3, "elig": 4}

        # * Other
        self.feature_col_names = self.make_feature_col_names()
        self.avg_pos_height_dict = self.avg_pos_ht_wt_dict(height=True)
        self.avg_pos_weight_dict = self.avg_pos_ht_wt_dict(height=False)

    def make_feature_col_names(self):  # Top Level
        """
        creating a list of all the feature columns that result from the run() method
        """
        cols = []
        for position in self.pos_num_dict:
            for i in range(self.pos_num_dict[position]):
                for stat in self.pos_stat_dict[position]:
                    position_name = f"{position}{i+1}_{stat}"
                    cols.append(position_name)
                cols += [f"{position}{i+1}_" + item for item in ["Height", "Weight", "Age", "Injury_Status"]]
        return cols

    def _avg_player_ht_wt(self, position, height=True):  # Helping Helper avg_pos_ht_wt_dict
        """
        computes the average player's height/weight at a position
        """
        ht_wt = "Height" if height else "Weight"
        rev_position = self.rev_pos_dict[position]
        position_df = self.player_df.loc[self.player_df['Position'] == rev_position]
        ht_wt_vals = list(position_df[ht_wt][position_df[ht_wt].notnull()])
        ht_wt_ints = [self._player_height(ht_wt_val, "") if height else self._player_weight(ht_wt_val, "") for ht_wt_val in ht_wt_vals]
        return sum(ht_wt_ints) / len(ht_wt_ints)

    def avg_pos_ht_wt_dict(self, height=True):  # Top Level
        ht_wt_dict = {}
        for position in self.positions:
            ht_wt_dict[position] = self._avg_player_ht_wt(position, height)
        return ht_wt_dict

    def _check_nan(self, val):  # Helping Helper _split_dash_slash_cols
        if isinstance(val, float):
            if np.isnan(val):
                return True
        if val is None:
            return True
        return False

    def _split_dash_slash_cols(self, player_stats_df, col, dash=True):  # Specific Helper load_clean_player_stats_df
        """
        retuns a dash/slash column, split into two (the value before and after the dash/slash)
        """
        dash_slash = '-' if dash else '/'
        col_vals = list(player_stats_df[col])
        splits = [val.split(dash_slash) if not self._check_nan(val) else (None, None) for val in col_vals]
        ds_col1 = [split[0] for split in splits]
        ds_col2 = [split[1] for split in splits]
        return ds_col1, ds_col2

    def load_clean_player_stats_df(self):  # Top Level
        """
        loads and cleans (split dash stats into separate cols) the player_stats_df
        """
        dash_stats = ["Times_Sacked"] if self.football_league else ["FG", "3PT", "FT"]
        slash_stats = ["Passing_Comp_Att", "FG_Made_Att", "XP_Made_Att"] if self.football_league else []
        player_stats_df = pd.read_csv(f"{ROOT_PATH}/Data/ESPN/{self.league}/Player_Stats.csv")
        # * splitting dash stats into two columns
        for dash_stat in dash_stats:
            dash_col1, dash_col2 = self._split_dash_slash_cols(player_stats_df, dash_stat, dash=True)
            player_stats_df.drop([dash_stat], axis=1, inplace=True)
            player_stats_df[dash_stat + "_d1"] = dash_col1
            player_stats_df[dash_stat + "_d2"] = dash_col2

        # * splitting slash stats into two columns
        for slash_stat in slash_stats:
            slash_col1, slash_col2 = self._split_dash_slash_cols(player_stats_df, slash_stat, dash=False)
            player_stats_df.drop([slash_stat], axis=1, inplace=True)
            player_stats_df[slash_stat + "_s1"] = slash_col1
            player_stats_df[slash_stat + "_s2"] = slash_col2

        return player_stats_df

    def player_ids(self, team, date, pre_scraping):  # Top Level
        """
        finding the player_id's for the team
        - locates the players who played if the game is pre_scraping
        - locates players on the roster who aren't "out" in the injury_df if post-scraping
        TODO this errors sometimes - could make sure it's good before running?
        """
        if pre_scraping:
            team_date_df = self.player_stats_df[(self.player_stats_df["Team"] == team) & (self.player_stats_df["Date"] == date)]
            player_ids = list(team_date_df["Player_ID"])
        else:
            input_dt = datetime.datetime.strptime(date, "%Y-%m-%d")
            team_roster_df = self.roster_df.loc[self.roster_df['Team'] == team]
            team_roster_dts = [datetime.datetime.strptime(scrape_ts, "%Y-%m-%d %H:%M") for scrape_ts in list(set(list(team_roster_df['scrape_ts'])))]
            most_recent_roster_scrape = max([scrape_ts for scrape_ts in team_roster_dts])  # if scrape_ts <= input_dt])
            most_recent_team_roster_df = team_roster_df.loc[team_roster_df['scrape_ts'] == most_recent_roster_scrape.strftime("%Y-%m-%d %H:%M")]
            player_ids = list(most_recent_team_roster_df["Player_ID"])
        return player_ids

    def _load_team_roster(self, team, date):  # Specific Helper  get_pos_dict_post_scraping
        """
        finding the most recent team roster from roster_df before a given date
        """
        df_before_date = self.roster_df.loc[(self.roster_df['Team'] == team)]  # & (self.roster_df['scrape_ts'] <= date)]
        most_recent_roster_scrape = list(df_before_date["scrape_ts"])[-1]
        roster_df = df_before_date.loc[df_before_date["scrape_ts"] == most_recent_roster_scrape]
        return roster_df

    def _load_team_injuries(self, team, date):  # Specific Helper  get_pos_dict_post_scraping
        """
        finding the most recent team injuries from injury_df before a given date
        """
        df_before_date = self.injury_df.loc[(self.injury_df['Team'] == team) & (self.injury_df['scraped_ts'] <= date)]
        most_recent_injury_scrape = list(df_before_date["scraped_ts"])[-1] if len(df_before_date) > 0 else list(self.injury_df['scraped_ts'])[-1]
        injury_df = df_before_date.loc[df_before_date["scraped_ts"] == most_recent_injury_scrape]
        return injury_df

    def _dash_name_injury_dict(self, roster_df, injury_df):  # Specific Helper id_injury_dict
        """
        building a dict of player_id's to injury status
        - starting out by giving everyone in the roster a 4 (healthy), then updating if injury_df differs
        """
        roster_dnames = [item.strip().lower().replace(' ', '-') for item in list(roster_df['Player'])]
        dash_name_injury_dict = {roster_dname: 4 for roster_dname in roster_dnames}
        for injury_dname, injury_status in zip(list(injury_df['Player']), list(injury_df['Status'])):
            status_first_word = injury_status.strip().split(' ')[0].lower()
            dash_name_injury_dict[injury_dname] = self.status_fw_to_num_dict[status_first_word]
        return dash_name_injury_dict

    # def _find_closest_dash_name(self, dash_name, roster_dash_names):  # Helping Helper _dash_name_to_player_id
    #     best_match = None
    #     best_match_dist = 1000
    #     for roster_dash_name in roster_dash_names:
    #         dist = lev.distance(dash_name, roster_dash_name)
    #         if dist < best_match_dist:
    #             best_match = roster_dash_name
    #             best_match_dist = dist

    #     print(f"Chagned {dash_name} to {best_match}")
    #     return best_match

    def _dash_name_to_player_id(self, covers_dash_name, roster_df):  # Specific Helper  id_injury_dict
        """
        returns the ESPN Player_ID for the dash_name input (dash_name comes from Covers!!)
        """
        roster_dash_names = [name.strip().lower().replace(' ', '-') for name in list(roster_df['Player'])]
        espn_dn_to_pid_dict = {dn: pid for dn, pid in zip(roster_dash_names, list(roster_df['Player_ID']))}
        if covers_dash_name in espn_dn_to_pid_dict:
            return espn_dn_to_pid_dict[covers_dash_name]
        elif covers_dash_name in self.player_matches:
            return self.player_matches[covers_dash_name]
        else:
            return "0"

    def id_injury_dict(self, player_ids, team, date, pre_scraping):  # Top Level
        """
        building a dict of {player_id: injury_status, ...}
        """
        if pre_scraping:
            return {player_id: 4 for player_id in player_ids}

        roster_df = self._load_team_roster(team, date)
        injury_df = self._load_team_injuries(team, date)
        dash_name_injury_dict = self._dash_name_injury_dict(roster_df, injury_df)
        id_injury_dict = {self._dash_name_to_player_id(dash_name, roster_df): dash_name_injury_dict[dash_name]
                          for dash_name in dash_name_injury_dict}
        return id_injury_dict

    def _find_player_position(self, player_id):  # Specific Helper pos_id_dict
        """
        given a player_id, this will find that player's position
        """
        player = self.player_df.loc[self.player_df['Player_ID'] == player_id]
        position = list(player['Position'])[0] if len(player) > 0 else None
        if position not in self.pos_dict or position is None:
            return None
        return self.pos_dict[position]

    def pos_id_dict(self, player_ids):  # Top Level
        """
        creates a position dict showing the player_id's available at each position
        - {pos: [pos_id, pos_id, pos_id], pos: [pos_id, ...], ...}
        """
        pos_id_dict = {position: [] for position in self.positions}
        player_positions = [self._find_player_position(player_id) for player_id in player_ids]
        for player_id, player_position in zip(player_ids, player_positions):
            if player_position is not None:
                pos_id_dict[player_position] += [player_id]
        return pos_id_dict

    def _player_past_stats(self, player_id, date, past_games, position):  # Specific Helper get_pos_stats_dict
        """
        returns a list of a player's average stats in past_games games before 'date' for stats
          we care about for their position
        """
        player_stats_df = self.player_stats_df.loc[(self.player_stats_df['Player_ID'] == player_id) & (self.player_stats_df['Date'] <= date)]
        player_stats_df = player_stats_df.iloc[-past_games:]
        position_stats = self.pos_stat_dict[position]
        position_stat_vals = []
        for stat in position_stats:
            stat_vals = list(player_stats_df[stat][player_stats_df[stat].notnull()])
            stat_vals = [int(stat_val) for stat_val in stat_vals]
            avg_stat_val = (sum(stat_vals) / len(stat_vals)) if len(stat_vals) > 0 else 0
            position_stat_vals.append(avg_stat_val)
        return position_stat_vals

    def _sort_pos_stats_dict(self, pos_stats_dict):  # Specific Helper get_pos_stats_dict
        """
        sorting the players' order in the pos_stats_dict so the players who play more show up first
        - basketball sorts by minutes
        - football sorts by size of the stats dict overall (rationale is that players who play more generate more stats)
        """
        if self.football_league:
            pos_stats_dict = {pos: sorted(pos_stats_dict[pos], key=lambda x: sum(x), reverse=True) for pos in pos_stats_dict}
        else:
            pos_stats_dict = {pos: sorted(pos_stats_dict[pos], key=lambda x: x[0], reverse=True) for pos in pos_stats_dict}
        return pos_stats_dict

    def _player_height(self, height_str, position):  # Helping Helper _player_bio_arr
        """
        returns the height of a player in inches (or the avg at that position if null)
        """
        if '"' not in height_str:
            return self._avg_player_ht_wt(position, height=True)
        feet = int(height_str.split("'")[0])
        inches = int(height_str.split(" ")[1].split('"')[0])
        return (feet * 12) + inches

    def _player_weight(self, weight_str, position):  # Helping Helper _player_bio_arr
        """
        returns the weight of a player in inches (or the avg at that position if null)
        """
        if "lbs" not in weight_str:
            return self._avg_player_ht_wt(position, height=False)
        weight = weight_str.strip().split(" ")[0]
        return int(weight)

    def _player_age(self, birthdate_str, date):  # Helping Helper _player_bio_arr
        """
        returns the player's age in years, or 21/26 if null
        """
        if "/" not in birthdate_str:
            return 21 if 'NCAA' in self.league else 26  # TODO update this to be better
        birthdate_str = birthdate_str.split(" (")[0]
        birthdate_dt = datetime.datetime.strptime(birthdate_str, "%m/%d/%Y")
        age = datetime.datetime.strptime(date, "%Y-%m-%d") - birthdate_dt
        return age.days / 365

    def _player_bio_arr(self, player_id, position, date):  # Specific Helper get_pos_stats_dict
        """
        returns a list of the player's height/weight/age, or the average at their position if null
        - [height, weight, age]
        """
        player = self.player_df.loc[self.player_df['Player_ID'] == player_id]
        height = str(player['Height'].values[0])
        weight = str(player['Weight'].values[0])
        birth_date = str(player['Birth_Date'].values[0])
        arr = [self._player_height(height, position), self._player_weight(weight, position), self._player_age(birth_date, date)]
        return arr

    def get_pos_stats_dict(self, team, date, past_games, position_id_dict, id_injury_dict):  # Top Level
        """
        - {pos: [pos_stats, pos_stats], pos: [pos_stats, ...], ...}
        """
        pos_stats_dict = {}
        for position in self.positions:
            player_ids = position_id_dict[position]
            stats_arrs = [self._player_past_stats(player_id, date, past_games, position) for player_id in player_ids]
            injury_status_arrs = [[id_injury_dict[player_id]] for player_id in player_ids]
            player_bio_arrs = [self._player_bio_arr(player_id, position, date) for player_id in player_ids]
            pos_stats_dict[position] = [stats_arr + bio_arr + injury_status_arr
                                        for stats_arr, bio_arr, injury_status_arr in
                                        zip(stats_arrs, player_bio_arrs, injury_status_arrs)]

        pos_stats_dict = self._sort_pos_stats_dict(pos_stats_dict)
        return pos_stats_dict

    def pos_stats_dict_to_player_data(self, position_stats_dict):
        """
        takes the position stats and creates an array of the team's player stats
        - uniform size - always the same shape (within the same sport)!
        """
        output = []
        for pos in self.pos_num_dict:
            for i in range(self.pos_num_dict[pos]):
                if len(position_stats_dict[pos]) > i:
                    new_data = position_stats_dict[pos][i]
                else:
                    new_data = [0] * len(self.pos_stat_dict[pos])
                    age = 21 if 'NCAA' in self.league else 25
                    new_data += [self.avg_pos_height_dict[pos], self.avg_pos_weight_dict[pos], age, 4]

                output += new_data
        return output

    def run(self, team, date, past_games=10):
        pre_scraping = datetime.datetime.strptime(date, "%Y-%m-%d") < datetime.datetime(2021, 11, 2)

        try:
            player_ids = self.player_ids(team, date, pre_scraping)
        except Exception as e:
            print(e)
            print(team, date)

        id_injury_dict = self.id_injury_dict(player_ids, team, date, pre_scraping)
        player_ids = [player_id for player_id in player_ids if ((player_id in id_injury_dict) and (id_injury_dict[player_id] != 0))]
        position_id_dict = self.pos_id_dict(player_ids)
        position_stats_dict = self.get_pos_stats_dict(team, date, past_games, position_id_dict, id_injury_dict)
        player_data_arr = self.pos_stats_dict_to_player_data(position_stats_dict)
        return player_data_arr


if __name__ == '__main__':
    league = "NFL"
    # player_id = "2330"  # Tom Brady
    x = Player_Data(league)
    self = x
    past_games = 10
    team = "Tampa Bay Buccaneers"
    date = "2021-10-10"
    player_data_arr = x.run("Tampa Bay Buccaneers", "2021-11-10")
    # x.run("Tampa Bay Buccaneers", "2021-11-30")
