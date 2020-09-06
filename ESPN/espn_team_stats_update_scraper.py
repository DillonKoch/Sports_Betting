# ==============================================================================
# File: espn_update_team_stats_scraper.py
# Project: ESPN
# File Created: Saturday, 5th September 2020 11:32:44 am
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 6th September 2020 12:01:59 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraper for updating team stats in finished games in each league's csv
# ==============================================================================


import argparse
from os.path import abspath, dirname
import sys
import pandas as pd
import datetime
import warnings
warnings.filterwarnings('ignore')

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN.espn_team_stats_scraper import Team_Stats_Scraper
from ESPN.espn_team_stats import Team_Stats


class Team_Stats_Update_Scraper:
    def __init__(self, league):
        self.league = league
        self.df_path = ROOT_PATH + f"/ESPN/Data/{self.league}.csv"
        self.football_league = True if self.league in ["NFL", "NCAAF"] else False
        self.stats_cols = Team_Stats().all_cols(self.football_league)

    def filter_games_with_stats(self, df):  # Top Level
        """
        filtering out games that already have team stats scraped
        """
        test_col = "home_first_downs" if self.football_league else "home_field_goals"
        new_df = df.loc[df[test_col].isnull()]
        return new_df

    def filter_by_date(self, df):  # Top Level
        """
        filtering out games that haven't happened yet
        """
        df['datetime'] = pd.to_datetime(df['datetime'])
        df['datetime'] = df['datetime'].dt.date
        today = datetime.date.today()
        new_df = df.loc[df.datetime < today]
        return new_df

    def filter_recent(self, df, recent_only):  # Top Level
        """
        filters out games from over 1 year ago if recent_only is True
        - sometimes ESPN doesn't have team stats for games in the past, so this
          skips those to just update the newer games
        """
        if not recent_only:
            return df

        df['datetime'] = pd.to_datetime(df['datetime'])
        df['datetime'] = df['datetime'].dt.date
        one_year_ago = datetime.date.today() - datetime.timedelta(days=365)
        recent_df = df.loc[df.datetime > one_year_ago]
        return recent_df

    def update_stats(self, original_df, update_df):  # Top Level
        """
        updating the team stats columns in the original df, based on the rows
        that qualified for update_df
        """
        ts_scraper = Team_Stats_Scraper(self.league)

        for i, row in update_df.iterrows():
            espn_id = int(row['ESPN_ID'])
            ts = ts_scraper.run(espn_id)
            stats_row = ts.make_row(self.football_league)
            print(f"\n{row['Home']} vs {row['Away']} - {row['Date']}\n")
            print(stats_row)
            original_df.loc[i, self.stats_cols] = stats_row
        return original_df

    def run(self, recent_only):  # Run
        original_df = pd.read_csv(self.df_path)
        update_df = self.filter_games_with_stats(original_df)
        update_df = self.filter_by_date(update_df)
        update_df = self.filter_recent(update_df, recent_only)
        final_df = self.update_stats(original_df, update_df)
        final_df.to_csv(self.df_path, index=False)
        print(f"\n{self.league} ESPN data saved!\n")
        return final_df


def parse_league(arg_list=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--league', help="One of NFL, NBA, NCAAF, NCAAB")
    parser.add_argument('--recent_only', action='store_true', default=True,
                        help="whether to scrape recent team stats only")
    if arg_list is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arg_list)

    args_dict = vars(args)
    league = args_dict['league']
    recent_only = args_dict['recent_only']
    return league, recent_only


if __name__ == '__main__':
    league, recent_only = parse_league()
    if recent_only:
        print("Only updating team stats for recent games")
    x = Team_Stats_Update_Scraper(league)
    self = x
    x.run(recent_only)
