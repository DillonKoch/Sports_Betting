# ==============================================================================
# File: espn_season_scraper.py
# Project: ESPN_Scrapers
# File Created: Saturday, 23rd May 2020 11:04:56 am
# Author: Dillon Koch
# -----
# Last Modified: Saturday, 29th August 2020 4:34:20 pm
# Modified By: Dillon Koch
# -----
#
# -----
# Scraping seasons from ESPN
# ==============================================================================

import json
import os
import re
import sys
import time
from os.path import abspath, dirname

import pandas as pd

ROOT_PATH = dirname(dirname(abspath(__file__)))
if ROOT_PATH not in sys.path:
    sys.path.append(ROOT_PATH)

from ESPN.espn_game_scraper import ESPN_Game_Scraper
from Utility.Utility import get_sp1


class ESPN_Season_Scraper:
    """
     Scrapes all historical data for each league into the ESPN_Data folder
     Can also scrape NBA Playoffs and upcoming seasons with other run methods
    """

    def __init__(self, league):
        self.league = league
        self.egs = ESPN_Game_Scraper(self.league)
        self.data_path = ROOT_PATH + '/ESPN/Data/{}'.format(self.league)
        self.q_amount = 2 if self.league == "NCAAB" else 4

    @property
    def config(self):  # Property  Tested
        with open(ROOT_PATH + "/ESPN/{}.json".format(self.league.lower())) as f:
            data = json.load(f)
        return data

    @property
    def game_link_re(self):  # Property  Tested
        re_dict = {
            "NBA": re.compile(r"http://www.espn.com/nba/game\?gameId=(\d+)"),
            "NFL": re.compile(r"http://www.espn.com/nfl/game/_/gameId/(\d+)"),
            "NCAAF": re.compile(r"http://www.espn.com/college-football/game/_/gameId/(\d+)"),
            "NCAAB": re.compile(r"http://www.espn.com/mens-college-basketball/game\?gameId=(\d+)")}
        return re_dict[self.league]

    def _make_season_df(self):  # Specific Helper scrape_season  Tested
        """
        creates initial season dataframe using the columns specified in the league's json file
        """
        cols = self.config["DF Columns"]
        df = pd.DataFrame(columns=cols)
        return df

    def _get_game_sections(self, team_abbrev, year, season_type=2):  # Specific Helper scrape_season  Tested
        """
        Scrapes the html from a team's season schedule webpage on ESPN, and
        returns the sections of the html including the season's games
        """
        base_link = self.config["Season Base Link"].format(
            team_abbrev=team_abbrev, year=year, season_type=season_type)
        sp = get_sp1(base_link)
        sections = sp.find_all('tr', attrs={'class': 'filled Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'filled bb--none Table__TR Table__TR--sm Table__even'})
        sections += sp.find_all('tr', attrs={'class': 'bb--none Table__TR Table__TR--sm Table__even'})
        return sections

    def _week_from_section(self, section):  # Helping Helper _link_week_from_game_section  Tested
        """
        ONLY TO BE USED FOR NFL GAMES TO GET THE WEEK - GAME DATES COME FROM ESPN_GAME_SCRAPER
        """
        td_htmls = section.find_all('td', attrs={'class': 'Table__TD'})
        week = td_htmls[0].get_text()
        return week

    def _link_from_game_section(self, section):  # Specific Helper scrape_season  Tested
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
        return link

    def _link_week_to_row(self, df, link, week, year):  # Specific Helper scrape_season
        game_id = self.game_link_re.search(link).group(1)
        game = self.egs.run(game_id)
        row = game.to_row_list(self.league, year, week)
        df.loc[len(df)] = row
        return df

    def scrape_season(self, team_abbrev, year, season_type=2):  # Top Level
        """
        Scrapes one team's season into a dataframe
        """
        df = self._make_season_df()
        game_sections = self._get_game_sections(team_abbrev, year, season_type)
        for i, section in enumerate(game_sections):
            print("{}/{}".format(i, len(game_sections)))
            week = self._week_from_section(section) if self.league == "NFL" else None
            link = self._link_from_game_section(section)
            if link is None:
                continue
            df = self._link_week_to_row(df, link, week, year)
            time.sleep(5)
        return df

    def _find_unscraped_playoff_years(self, team):  # Specific Helper scrape_nba_playoffs
        """
        finds the years an nba team's playoff data hasn't been scraped yet
        """
        team_csvs = os.listdir(ROOT_PATH + "/ESPN/Data/NBA/{}/".format(team))
        playoff_csvs = [item for item in team_csvs if '.csv' in item and "playoff" in item]
        playoff_csv_years = [item[-8:-4] for item in playoff_csvs]
        all_years = [str(item) for item in list(range(1993, 2021, 1))]
        unscraped_years = [item for item in all_years if item not in playoff_csv_years]
        return unscraped_years

    def scrape_nba_playoffs(self):  # Run
        """
        ONLY USED FOR NBA SINCE THEIR PLAYOFF GAMES ARE ON A SEPARATE PAGE ON ESPN
        """
        teams = [item[0] for item in self.config["Teams"]]
        team_abbrevs = [item[1] for item in self.config["Teams"]]
        all_years = [str(item) for item in list(range(1993, 2021, 1))]

        for team, abrev in zip(teams, team_abbrevs):
            unscraped_years = self._find_unscraped_playoff_years(team)
            years = [item for item in all_years if item in unscraped_years]
            for year in years:
                try:
                    print("Scraping {} {} playoffs data...".format(team, year))
                    df = self.scrape_season(abrev, year, 3)
                    year1, year2 = self._get_years(year)
                    df.to_csv(ROOT_PATH + "/ESPN/Data/NBA/{}/{}_playoffs_{}-{}.csv".format(team, team, year1, year2))
                except Exception as e:
                    print(e)
                    print("Error scraping {} {} playoffs data, moving on...".format(team, year))
                    time.sleep(30)

    def find_years_unscraped(self, team_name):  # Top Level
        """
        finds years a team's season data hasn't been scraped yet
        """
        path = ROOT_PATH + "/ESPN/Data/{}/{}/".format(self.league, team_name)
        beginning_year = 2006
        all_years = [str(item) for item in list(range(beginning_year, 2021, 1))]
        years_found = []
        year_comp = re.compile(r"(\d{4}).csv")
        for filename in os.listdir(path):
            if "playoff" not in filename:
                match = re.search(year_comp, filename)
                if match:
                    year = match.group(1)
                    years_found.append(year)
        return [item for item in all_years if item not in years_found]

    def _get_years(self, year):  # Specific Helper scrape_team_history
        """
        returns the two years to use in a csv name (e.g. Iowa_2018-2019.csv)
        seasons are referred to differently in NFL/NCAAF and NBA/NCAAB, so this is needed
        """
        year = int(year)
        if self.league in ["NFL", "NCAAF"]:
            year1 = year
            year2 = year + 1
        else:
            year1 = year - 1
            year2 = year
        return year1, year2

    def scrape_team_history(self, team_abbrev, name):  # Run
        """
        Scrapes the entire history of a team's games according to the years_unscraped
        """
        years_unscraped = self.find_years_unscraped(name)
        for year in years_unscraped:
            print("Scraping data for {} {}".format(name, year))
            df = self.scrape_season(team_abbrev, year)
            year1, year2 = self._get_years(year)
            path = ROOT_PATH + "/ESPN/Data/{}/{}/{}_{}-{}.csv".format(self.league, name, name, year1, year2)
            df.to_csv(path, index=False)

    def scrape_all_leauge_history(self):  # Run
        """
        runs scrape_team_history for all teams in a league
        """
        team_abbrevs = [item[1] for item in self.config["Teams"]]
        names = [item[0] for item in self.config["Teams"]]
        for team_abbrev, name in zip(team_abbrevs, names):
            try:
                self.scrape_team_history(team_abbrev, name)
            except Exception as e:
                print(e)
                print("Error scraping, moving on to the next team")
                time.sleep(30)


if __name__ == "__main__":
    nfl = ESPN_Season_Scraper("NFL")
    nba = ESPN_Season_Scraper("NBA")
    ncaaf = ESPN_Season_Scraper("NCAAF")
    ncaab = ESPN_Season_Scraper("NCAAB")
    ncaab.scrape_all_leauge_history()
