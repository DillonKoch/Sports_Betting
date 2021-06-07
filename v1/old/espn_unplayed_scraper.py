# ==============================================================================
# File: espn_unplayed_scraper.py
# Project: ESPN_Scrapers
# File Created: Monday, 29th June 2020 3:17:15 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 29th August 2020 4:34:41 pm
# Modified By: Dillon Koch
# -----
#
# -----
# ESPN scraper inheriting from ESPN_Season_Scraper to scrape upcoming games
# ==============================================================================


import argparse
import datetime
import sys
import time
from os.path import abspath, dirname

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN.espn_season_scraper import ESPN_Season_Scraper
from Utility.Utility import sort_df_by_dt


class ESPN_Unplayed_Scraper(ESPN_Season_Scraper):
    """
    scrapes data for games that have not been played yet and updates teams' csv's
    - these games will need to be updated once the game is played by the update_results file
    - they could also be updated soon before the game to update the teams' records
    """

    def _scrape_team_unplayed_games(self, abbrev, year, current_espn_ids, season_type):  # Top Level
        """
        scrapes the unplayed games coming up for one team and returns them in a dataframe
        """
        df = self._make_season_df()
        game_sections = self._get_game_sections(abbrev, year, season_type)
        for section in game_sections:
            week = self._week_from_section(section) if self.league == "NFL" else None
            link = self._link_from_game_section(section)
            if link is None:
                continue
            current_game_id = self.game_link_re.search(link).group(1)
            if current_game_id not in current_espn_ids:
                df = self._link_week_to_row(df, link, week, year)
                print("found new {} game {}".format(abbrev, current_game_id))
                time.sleep(5)

        null_cols = ["Final_Status", "HQ1", "HQ2", "HQ3", "HQ4", "HOT", "AQ1", "AQ2", "AQ3",
                     "AQ4", "AOT", "H1H", "H2H", "A1H", "A2H"]
        for i, row in df.iterrows():
            if "Final" not in str(row['Final_Status']):
                for col in null_cols:
                    if col in list(df.columns):
                        row[col] = None
        time.sleep(3)
        print("{} new games found".format(len(df)))
        return df

    def scrape_unplayed_games(self, year=None, season_type=2):  # Run
        """
        scrapes all the unplayed games for a league and adds them to the teams' csv's
        """
        team_combos = self.config["Teams"]
        year = datetime.date.today().year if year is None else year

        for team in team_combos:
            print("Scraping new games for {}".format(team[0]))
            try:
                team_name, abbrev = team
            except BaseException:
                team_name, abbrev, conf = team  # ncaa jsons have conferences too
                print(team_name, abbrev, conf)
            current_df_path = ROOT_PATH + "/ESPN/Data/{}/{}.csv".format(self.league, team_name.replace(' ', '_'))
            current_df = pd.read_csv(current_df_path)
            current_df = current_df.loc[current_df.ESPN_ID.notnull(), :]
            current_espn_ids = [str(int(item)) for item in list(current_df.ESPN_ID)]

            try:
                new_df = self._scrape_team_unplayed_games(abbrev, year, current_espn_ids, season_type)
                current_df = pd.concat([current_df, new_df])
                current_df = sort_df_by_dt(current_df, keep_dt=True)
                current_df.to_csv(current_df_path, index=False)
            except BaseException:
                print("ERROR SCRAPING, MOVING ON")
                time.sleep(30)


def parse_args(arg_list=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--league', help="HELP_MSG")
    parser.add_argument('--season_type', help="HELP_MSG")
    parser.add_argument('--year', help="HELP_MSG")

    if arg_list is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arg_list)

    args_dict = vars(args)
    season_type = args_dict['season_type']
    league = args_dict['league']
    year = args_dict['year']
    return season_type, league, year


if __name__ == "__main__":
    season_type, league, year = parse_args()
    season_type = 2 if season_type is None else season_type
    print("Scraping {} {}, with season type {}".format(league, year, season_type))

    x = ESPN_Unplayed_Scraper(league)
    x.scrape_unplayed_games(year, season_type)
