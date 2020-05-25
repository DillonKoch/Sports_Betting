# ==============================================================================
# File: espn_season_scraper.py
# Project: Sports_Betting
# File Created: Tuesday, 14th April 2020 5:08:27 pm
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 23rd May 2020 11:04:12 am
# Modified By: Dillon Koch
# -----
#
#
# -----
# Scraper to get all season-long data for each league
# ==============================================================================

import json
import os
import re
import sys
import time
from os.path import abspath, dirname

import pandas as pd
from func_timeout import func_set_timeout
from tqdm import tqdm

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from espn_game_scraper import ESPN_Game_Scraper
from Utility import get_sp1, null_if_error


class ESPN_Season_Scraper:
    def __init__(self):
        self.egs = ESPN_Game_Scraper()
        self.root_path = ROOT_PATH + '/'

    @property
    def json_data(self):  # Global Helper Tested NBA
        with open("{}.json".format(self.league.lower())) as f:
            data = json.load(f)
        return data

    def _get_game_sections(self, team_abbrev, year, season_type=2):  # Specific Helper team_dates_links Tested NBA
        base_link = self.json_data["Season Base Link"].format(
            team_abbrev=team_abbrev, year=year, season_type=season_type)
        sp = get_sp1(base_link)
        sections = sp.find_all('tr', attrs={'class': 'filled Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'filled bb--none Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'bb--none Table__TR Table__TR--sm Table__even'})
        return sections

    @null_if_error(2)  # FIXME
    def _link_gameid_from_section(self, sp_section):  # Specific Helper team_dates_links  Tested NBA
        td_htmls = sp_section.find_all('td', attrs={'class': 'Table__TD'})
        for html in td_htmls:
            match = re.search(self.re_game_link, str(html))
            if match:
                link = match.group(0)
                game_id = match.group(1)
        return link, game_id

    def team_gameid_links(self, team_abbrev, year, season_type=2):  # Helping Helper _full_season_df  Tested NBA
        game_sections = self._get_game_sections(team_abbrev, year, season_type)
        games = []
        for section in game_sections:
            link, game_id = self._link_gameid_from_section(section)
            if game_id == 'NULL':
                continue
            games.append((link, game_id))
        return games

    def _make_season_df(self):  # Helping Helper _full_season_df  Tested NBA
        cols = self.json_data["DF Columns"]
        df = pd.DataFrame(columns=cols)
        return df

    def _game_to_row(self, season, game):  # Helping Helper _full_season_df
        q_amount = 4 if self.league != "NCAAB" else 2
        row = [game.ESPN_ID, season, game.game_date, game.home_name, game.away_name,
               game.home_record, game.away_record,
               game.home_score, game.away_score, game.line, game.over_under,
               game.final_status, game.network]

        for scores in [game.home_qscores, game.away_qscores]:
            row += [item for item in scores]
            if len(scores) == q_amount:
                row += ["NULL"]

        row.append(self.league)
        return row

    @func_set_timeout(7 * 60)
    def _full_season_df(self, team_abbrev, year, season_type=2):  # Specific Helper scrape_team_history
        game_tuples = self.team_gameid_links(team_abbrev, year, season_type)
        df = self._make_season_df()
        for gt in tqdm(game_tuples):
            game = self.all_game_info_func(gt[1])
            row = self._game_to_row(year, game)
            df.loc[len(df)] = row
            time.sleep(2)
        return df

    def scrape_team_history(self, team_abbrev, years, season_type=2):  # Top Level
        for year in years:
            print("Scraping {} {} data...".format(year, team_abbrev))
            df = self._full_season_df(team_abbrev, year, season_type)
            path = "./Data/{}/{}/{}_{}.csv".format(self.league, team_abbrev, team_abbrev, year)
            df.to_csv(path)

    def find_years_unscraped(self, team_abbrev):  # Top Level
        path = "../Data/{}/{}/".format(self.league, team_abbrev)
        all_years = [str(item) for item in list(range(1993, 2021, 1))]
        years_found = []
        year_comp = re.compile(r"\d{4}")
        for filename in os.listdir(path):
            match = re.search(year_comp, filename)
            if match:
                year = match.group(0)
                years_found.append(year)
        return [item for item in all_years if item not in years_found]

    def run_all_season_scrapes(self):  # Run
        team_abbrevs = [item[1] for item in self.json_data["Teams"]]

        for team in team_abbrevs:
            try:
                years = self.find_years_unscraped(team)
                self.scrape_team_history(team, years)
            except BaseException:
                print('error with scraping!')
                for i in range(120):
                    print('sleeping for {} more seconds...'.format(120 - i))
                    time.sleep(1)


if __name__ == "__main__":
    ess = ESPN_Season_Scraper()
