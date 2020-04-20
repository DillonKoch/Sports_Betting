# ==============================================================================
# File: espn_season_scraper.py
# Project: Sports_Betting
# File Created: Tuesday, 14th April 2020 5:08:27 pm
# Author: Dillon Koch
# -----
# Last Modified: Monday, 20th April 2020 1:42:18 pm
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
import time

import pandas as pd
from tqdm import tqdm

from espn_game_scraper import ESPN_Game_Scraper
from Utility import dt_from_date_str, get_sp1, null_if_error


class ESPN_Season_Scraper:
    def __init__(self):
        self.egs = ESPN_Game_Scraper()

        self.root_path = "/home/allison/Documents/GITHUB/Sports_Betting/"
        self.nba_folder = "Data/NBA"
        self.nfl_folder = "Data/NFL"
        self.ncaaf_folder = "Data/NCAAF"
        self.ncaab_folder = "Data/NCAAB"

        self.re_comps = {"NBA": re.compile(r"http://www.espn.com/nba/game\?gameId=(\d+)"),
                         "NFL": re.compile(r'href')}

    @property
    def json_data(self):
        with open("season_data.json") as f:
            data = json.load(f)
        return data

    def _get_game_sections(self, league, team_abbrev, year, season_type=2):
        """
        _get_game_sections gets the html for each row in a team's season schedule

        Args:
            league (str): [description]
            team_abbrev (str): abbreviation for the team whose data you want
            year (str): season you want data for (year indicates the year the season ends in)
            season_type (int, optional): 1=preseason, 2=regular season, 3=postseason. Defaults to 2.

        Returns:
            [type]: [description]
        """
        base_link = self.json_data[league]["Season Base Link"].format(team_abbrev, year, season_type)
        # base_link = self.json_data[league]["Season Base Link"] + team_abbrev + '/season/' + str(year)
        # base_link += "/seasontype/{}".format(season_type)
        sp = get_sp1(base_link)
        sections = sp.find_all('tr', attrs={'class': 'filled Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'filled bb--none Table__TR Table__TR--sm Table__even'})
        return sections

    def _game_date_from_section(self, sp_section):
        """
        _game_date_from_section finds the game date in a section from _get_game_sections

        Args:
            sp_section (BeautifulSoup): section of code for one game

        Returns:
            str/None: game date string or None if the result is "Date"
        """
        td_htmls = sp_section.find_all('td', attrs={'class': 'Table__TD'})
        result = td_htmls[0].get_text()
        return result if result != 'Date' else None

    @null_if_error(2)
    def _link_gameid_from_section(self, league, sp_section):
        td_htmls = sp_section.find_all('td', attrs={'class': 'Table__TD'})
        for html in td_htmls:
            match = re.search(self.re_comps[league], str(html))
            if match:
                link = match.group(0)
                game_id = match.group(1)
        return link, game_id

    def team_dates_links(self, league, team_abbrev, year):
        game_sections = self._get_game_sections(league, team_abbrev, year)
        games = []
        for section in game_sections:
            game_date = self._game_date_from_section(section)
            if game_date is None:
                continue
            link, game_id = self._link_gameid_from_section(league, section)
            games.append((game_date, link, game_id))
        return games

    def _make_season_df(self, league):
        cols = self.json_data[league]["DF Columns"]
        df = pd.DataFrame(columns=cols)
        return df

    def _game_to_row(self, df, game, periods=4):  # need season/date because we can't get it from game summary :(
        row = [game.home_name, game.away_name, game.home_record, game.away_record,
               game.home_score, game.away_score,
               game.line, game.over_under, game.final_status, game.network]

        home_qscores = [item for item in game.home_qscores]
        if len(home_qscores) == periods:
            home_qscores.append('NULL')
        row += home_qscores

        away_qscores = [item for item in game.away_qscores]
        if len(away_qscores) == periods:
            away_qscores.append('NULL')
        row += away_qscores

        row.append(game.league)
        return row

    def full_season_df(self, league, team_abbrev, year):
        egs = ESPN_Game_Scraper()
        game_tuples = self.team_dates_links(league, team_abbrev, year)
        df = self._make_season_df(league)
        for gt in tqdm(game_tuples):
            game = egs.all_nba_info(gt[2])
            row = [gt[2], year, gt[0]] + self._game_to_row("NBA", game)
            df.loc[len(df)] = row
            time.sleep(2)
        return df

    def scrape_team_history(self, league, team_abbrev, years):
        for year in years:
            print("Scraping {} {} data...".format(year, team_abbrev))
            df = self.full_season_df(league, team_abbrev, year)
            path = "./Data/{}/{}/{}_{}.csv".format(league, team_abbrev, team_abbrev, year)
            df.to_csv(path)

    def find_years_unscraped(self, league, team_abbrev):
        path = "./Data/{}/{}/".format(league, team_abbrev)
        all_years = [str(item) for item in list(range(1993, 2021, 1))]
        years_found = []
        year_comp = re.compile(r"\d{4}")
        for filename in os.listdir(path):
            match = re.search(year_comp, filename)
            if match:
                year = match.group(0)
                years_found.append(year)
        return [item for item in all_years if item not in years_found]


if __name__ == "__main__":
    ess = ESPN_Season_Scraper()
    egs = ESPN_Game_Scraper()

    # heat_games = ess.team_dates_links('NBA', 'mia')
    # df = ess._make_season_df("NBA")
    # game = egs.all_nba_info(heat_games[0][2])
    # row = list('sdf') + ess._game_to_row(df, game)
    # df = ess.full_season_df("NBA", 'mia', '2019')
    # ess.scrape_team_history("NBA", "mia", list(range(1999, 2019, 1)))
    # time_left = 60 * 160
    # for i in range(time_left):
    #     time.sleep(1)
    #     print("{} seconds left".format(time_left - i))
    # for team in ess.json_data["NBA"]["Abbreviations"][:10]:
    #     ess.scrape_team_history("NBA", team, list(range(1993, 2021, 1)))
    team = 'cle'
    years = ess.find_years_unscraped("NBA", team)

    ess.scrape_team_history("NBA", team, years)
