# ==============================================================================
# File: espn_change_team_name.py
# Project: ESPN
# File Created: Sunday, 6th September 2020 3:27:29 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 6th September 2020 5:57:37 pm
# Modified By: Dillon Koch
# -----
#
# -----
# changes a team's name in the leauge .csv if the team's name changes
# San Diego Chargers -> Los Angeles
# Washington Redskins -> Football team, etc
# ==============================================================================

from os.path import abspath, dirname
import sys
import pandas as pd
import argparse
import warnings
warnings.filterwarnings('ignore')

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)


class ESPN_Change_Name:
    def __init__(self, league):
        self.league = league
        self.df_path = ROOT_PATH + f"/ESPN/Data/{self.league}.csv"

    def run(self, old_name, new_name):  # Run
        df = pd.read_csv(self.df_path)
        df['Home'] = df['Home'].replace(old_name, new_name)
        df['Away'] = df['Away'].replace(old_name, new_name)
        df.to_csv(self.df_path, index=False)
        print(f"Changed name {old_name} to {new_name} in {self.league} data!")
        return df


def parse_args(arg_list=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--league', help="league to change name for")
    parser.add_argument('--old_name', help="Old team name to be changed")
    parser.add_argument('--new_name', help="new team name to replace old name")

    if arg_list is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arg_list)

    args_dict = vars(args)
    league = args_dict['league']
    old_name = args_dict['old_name']
    new_name = args_dict['new_name']
    return league, old_name, new_name


if __name__ == '__main__':
    league, old_name, new_name = parse_args()
    x = ESPN_Change_Name(league)
    self = x
    x.run(old_name, new_name)
