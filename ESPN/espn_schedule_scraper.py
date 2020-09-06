# ==============================================================================
# File: espn_schedule_scraper.py
# Project: ESPN
# File Created: Saturday, 5th September 2020 5:14:59 pm
# Author: Dillon Koch
# -----
# Last Modified: Sunday, 6th September 2020 2:06:48 pm
# Modified By: Dillon Koch
# -----
#
# -----
# scraper to update each league's csv with the current/upcoming season schedule
# ==============================================================================


import argparse
import datetime
import json
import re
import sys
import time
from os.path import abspath, dirname
import warnings
warnings.filterwarnings('ignore')

import pandas as pd


ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN.espn_game_scraper import ESPN_Game_Scraper
from Utility.Utility import get_sp1, sort_df_by_dt


class Schedule_Scraper:
    def __init__(self, league):
        self.league = league
        self.df_path = ROOT_PATH + f"/ESPN/Data/{self.league}.csv"
        self.egs = ESPN_Game_Scraper(self.league)

    @property
    def game_link_re(self):  # Property
        re_dict = {
            "NBA": re.compile(r"http://www.espn.com/nba/game\?gameId=(\d+)"),
            "NFL": re.compile(r"http://www.espn.com/nfl/game/_/gameId/(\d+)"),
            "NCAAF": re.compile(r"http://www.espn.com/college-football/game/_/gameId/(\d+)"),
            "NCAAB": re.compile(r"http://www.espn.com/mens-college-basketball/game\?gameId=(\d+)")}
        return re_dict[self.league]

    def _load_team_info(self):  # Specific Helper get_new_espn_id_week_pairs
        """
        loads all the team lists from the league's config file
        - NFL/NBA teams have [[team, team_abbrev], [team, team_abbreb], ...]
        - NCAA teams have [[team, team_abbrev, conference], ...]
        """
        with open(ROOT_PATH + "/ESPN/{}.json".format(self.league.lower())) as f:
            data = json.load(f)
        return data['Teams']

    def _get_base_link(self, team_abbrev, year, season_type):  # Helping Helper _get_game_sections
        """
        provides the base link for a team's schedule on ESPN in a given year and season type
        """
        link_dict = {
            "NFL": "https://www.espn.com/nfl/team/schedule/_/name/{team_abbrev}/season/{year}",
            "NBA": "https://www.espn.com/nba/team/schedule/_/name/{team_abbrev}/season/{year}/seasontype/{season_type}",
            "NCAAF": "https://www.espn.com/college-football/team/schedule/_/id/{team_abbrev}/season/{year}",
            "NCAAB": "https://www.espn.com/mens-college-basketball/team/schedule/_/id/{team_abbrev}/season/{year}"
        }
        return link_dict[self.league].format(team_abbrev=team_abbrev, year=year, season_type=season_type)

    def _get_game_sections(self, team_abbrev, year, season_type=2):  # Specific Helper get_new_espn_id_week_pairs
        """
        Scrapes the html from a team's season schedule webpage on ESPN, and
        returns the sections of the html including the season's games
        """
        base_link = self._get_base_link(team_abbrev, year, season_type)
        sp = get_sp1(base_link)
        time.sleep(3)
        sections = sp.find_all('tr', attrs={'class': 'filled Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'filled bb--none Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'bb--none Table__TR Table__TR--sm Table__even'})
        return sections

    def _week_from_section(self, section):  # Specific Helper get_new_espn_id_week_pairs
        """
        ONLY TO BE USED FOR NFL GAMES TO GET THE WEEK - GAME DATES COME FROM ESPN_GAME_SCRAPER
        """
        if self.league != "NFL":
            return None
        td_htmls = section.find_all('td', attrs={'class': 'Table__TD'})
        week = td_htmls[0].get_text()
        return week

    def _espn_id_from_game_section(self, section):  # Specific Helper get_new_espn_id_week_pairs
        """
        finds the link to a game on ESPN (if it exists) from a section of
        a team's season webpage
        """
        link = None
        td_htmls = section.find_all('td', attrs={'class': 'Table__TD'})
        for html in td_htmls:
            match = re.search(self.game_link_re, str(html))
            if match:
                link = match.group(0)
        espn_id = link[-9:] if link is not None else None
        return espn_id

    def get_new_espn_id_week_pairs(self, year, season_type):  # Top Level
        """
        season types: preseason (1), regular season (2), playoffs (3)

        using the team info, this method finds all the espn_id-week pairs for the
        season
        - these pairs are used to update the league's .csv
        """

        teams_info = self._load_team_info()
        id_week_pairs = []
        for i, team in enumerate(teams_info):
            team_name = team[0]
            team_abbrev = team[1]
            print(f"{i}/{len(teams_info)} - {team_name}")

            sections = self._get_game_sections(team_abbrev, year, season_type)
            weeks = [self._week_from_section(section) for section in sections]
            espn_ids = [self._espn_id_from_game_section(section) for section in sections]
            espn_ids = [i for i in espn_ids if i is not None]
            new_pairs = [(espn_id, week) for espn_id, week in zip(espn_ids, weeks)]
            id_week_pairs += new_pairs
        id_week_pairs = list(set(id_week_pairs))
        return id_week_pairs

    def _pad_nones(self, df, row):  # Specific Helper add_game_to_df
        """
        adding None's to the end of the row provided by the ESPN_Game_Scraper
        to take the place of team stats that will be updated later
        """
        num_df_cols = len(list(df.columns))
        while len(row) < num_df_cols:
            row.append(None)
        return row

    def add_game_to_df(self, df, espn_id, week):  # Top Level
        """
        given the ongoing league .csv and an espn_id-week combo,
        this method adds the game to the csv
        """
        try:
            game = self.egs.run(espn_id)
            row = game.to_row_list(self.league, year, week)
            row = self._pad_nones(df, row)
            df.loc[len(df)] = row
            print(f"Added {game.home_name} vs {game.away_name} ({game.game_date})")
            return df
        except BaseException:
            print('-' * 25)
            print('ERROR SCRAPING GAME - {}'.format(espn_id))
            print('-' * 25)
            return df

    def run(self, year, season_type):  # Run
        original_df = pd.read_csv(self.df_path)
        original_ids = list(original_df['ESPN_ID'])
        original_ids = [str(item) for item in original_ids]

        new_id_week_pairs = self.get_new_espn_id_week_pairs(year, season_type)
        scrape_pairs = [pair for pair in new_id_week_pairs if pair[0] not in original_ids]
        # TODO figure out how to find the ID's to take out of df here (game 5-7s)
        i = 0
        for pair in scrape_pairs:
            espn_id, week = pair
            original_df = self.add_game_to_df(original_df, espn_id, week)

            print(f"{i}/{len(scrape_pairs)}")
            i += 1
            time.sleep(5)

        original_df = sort_df_by_dt(original_df, keep_dt=True)
        original_df.to_csv(self.df_path, index=False)
        print(f"Scraped {len(scrape_pairs)} new {self.league} games and saved csv!")
        return original_df

    def remove_unplayed_games(self):  # Top Level
        """
        removing games that are not played for whatever reason from the leauge .csv
        - this could remove a game 5-7 not played in an NBA series, cancelled games, etc
        """
        # if the game date is before today and final status doesn't have "Final"
        pass


def parse_args(arg_list=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--league', help="league to scrape games for")
    parser.add_argument('--year', help='Year of games to scrape')
    parser.add_argument('--season_type', help='Season type to scrape for')
    if arg_list is None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(arg_list)

    args_dict = vars(args)
    league = args_dict['league']
    year = args_dict['year']
    season_type = args_dict['season_type']
    return league, year, season_type


if __name__ == '__main__':
    league, year, season_type = parse_args()
    year = datetime.date.today().year if year is None else year
    season_type = 2 if season_type is None else season_type

    print(f"Scraping unplayed {league} games in {year} with season type {season_type}")

    # league = "NBA"
    # year = 2020
    x = Schedule_Scraper(league)
    self = x
    x.run(year, season_type)

    # TODO need to get rid of game 5-7s that don't get played too!
